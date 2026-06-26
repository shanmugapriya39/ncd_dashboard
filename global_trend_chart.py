import pandas as pd, json
 
bp  = pd.read_excel("cw1 -dataset.xlsx", sheet_name="Raised Blood Pressure")
bmi = pd.read_excel("cw1 -dataset.xlsx", sheet_name="BMI")
dia = pd.read_excel("cw1 -dataset.xlsx", sheet_name="Diabetes")
for d, name in [(bp,"Blood Pressure"),(bmi,"Obesity"),(dia,"Diabetes")]:
    d.columns = ["Country","Sex","Year","Prevalence"]
    d["Indicator"] = name
df = pd.concat([bp,bmi,dia], ignore_index=True)
df["Prevalence_pct"] = (df["Prevalence"]*100).round(1)
wb = pd.read_excel("CLASS_2025_10_07.xlsx", sheet_name="List of economies")
wb = wb[["Economy","Region","Income group"]].dropna(subset=["Region"])
wb.columns = ["Country","WB_Region","Income_group"]
df = df.merge(wb, on="Country", how="left")
df["WB_Region"] = df["WB_Region"].fillna("Unknown")
region_names = {
    "Middle East, North Africa, Afghanistan & Pakistan":"MENA",
    "Europe & Central Asia":"Europe & C. Asia",
    "East Asia & Pacific":"East Asia & Pacific",
    "Latin America & Caribbean":"Latin America",
    "Sub-Saharan Africa":"Sub-Saharan Africa",
    "South Asia":"South Asia",
    "North America":"North America",
}
df["WB_Region"] = df["WB_Region"].replace(region_names)
time_trend = (
    df[df["WB_Region"]!="Unknown"]
    .groupby(["Year","WB_Region","Indicator"])["Prevalence_pct"]
    .median().round(1).reset_index()
)
time_trend.columns = ["Year","Region","Indicator","value"]
data_json = json.dumps(time_trend.to_dict(orient="records"))
 
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:transparent;color:#0b0b0b}}
#controls{{display:flex;gap:10px;align-items:center;margin-bottom:10px}}
#controls label{{font-size:12px;color:#52514e}}
#indicatorSel{{font-size:12px;padding:4px 8px;border:1px solid #d3d1c7;border-radius:6px;background:#fff;cursor:pointer}}
#hint{{font-size:11px;color:#898781;margin-left:4px}}
#wrap{{position:relative}}
#tooltip{{
  position:absolute;
  width:215px;
  background:rgba(255,255,255,0.97);
  border:1px solid #d3d1c7;
  border-radius:10px;
  padding:12px 14px 10px;
  pointer-events:none;
  z-index:20;
  display:none;
  box-shadow:0 3px 14px rgba(0,0,0,0.11);
}}
#ttYear{{font-size:28px;font-weight:700;font-family:Georgia,serif;color:#0b0b0b;line-height:1}}
#ttUnit{{font-size:11px;color:#898781;margin-bottom:8px;margin-top:2px}}
.tt-row{{display:flex;justify-content:space-between;align-items:center;padding:3px 5px;border-radius:5px;margin-bottom:2px}}
.tt-left{{display:flex;align-items:center;gap:7px}}
.tt-dot{{width:9px;height:9px;border-radius:50%;flex-shrink:0}}
.tt-name{{font-size:12px}}
.tt-val{{font-size:13px;font-weight:600;font-family:Georgia,serif}}
#legend{{display:flex;flex-wrap:wrap;gap:6px 14px;margin-top:8px;font-size:11px}}
.leg-item{{display:flex;align-items:center;gap:5px}}
</style>
</head>
<body>
<div id="controls">
  <label for="indicatorSel">Indicator</label>
  <select id="indicatorSel">
    <option value="Blood Pressure">Blood Pressure</option>
    <option value="Obesity">Obesity</option>
    <option value="Diabetes">Diabetes</option>
  </select>
  <span id="hint">Hover chart to see ranked snapshot</span>
</div>
<div id="wrap">
  <svg id="chart" style="width:100%;display:block"></svg>
  <div id="tooltip">
    <div id="ttYear"></div>
    <div id="ttUnit">in %</div>
    <div id="ttRows"></div>
  </div>
</div>
<div id="legend"></div>
 
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
<script>
const RAW = {data_json};
 
const COLORS = {{
  'MENA':'#1D9E75','North America':'#4C78A8','Europe & C. Asia':'#F58518',
  'East Asia & Pacific':'#E45756','Latin America':'#72B7B2',
  'Sub-Saharan Africa':'#B279A2','South Asia':'#BAB0AC'
}};
const MUTED = {{
  'North America':'#8fb5d4','Europe & C. Asia':'#f8ba7e',
  'East Asia & Pacific':'#ec9a99','Latin America':'#a5d6d6',
  'Sub-Saharan Africa':'#ccb0c7','South Asia':'#d4d0cd'
}};
 
const regions = Object.keys(COLORS);
const years = [...new Set(RAW.map(d=>d.Year))].sort((a,b)=>a-b);
let currentInd = 'Blood Pressure';
let lastSnap = 2000;
 
function getByRegion(ind){{
  const m={{}};
  RAW.filter(d=>d.Indicator===ind).forEach(d=>{{
    if(!m[d.Region])m[d.Region]={{}};
    m[d.Region][d.Year]=d.value;
  }});
  return m;
}}
 
// SVG dimensions (viewBox units — no pixels needed for positioning)
const ML=48,MT=16,MR=85,MB=38;
const VW=640,VH=300; // viewBox width/height of plot area
const TOTAL_W=VW+ML+MR, TOTAL_H=VH+MT+MB;
 
const svg = d3.select('#chart').attr('viewBox',`0 0 ${{TOTAL_W}} ${{TOTAL_H}}`);
const g = svg.append('g').attr('transform',`translate(${{ML}},${{MT}})`);
 
const xSc = d3.scaleLinear().domain([1975,2016]).range([0,VW]);
const ySc = d3.scaleLinear().range([VH,0]);
 
const xAxisG=g.append('g').attr('transform',`translate(0,${{VH}})`);
const yAxisG=g.append('g');
const gridG=g.append('g');
const linesG=g.append('g');
const labelsG=g.append('g');
const dotsG=g.append('g');
 
const rule=g.append('line')
  .attr('y1',0).attr('y2',VH)
  .attr('stroke','#999').attr('stroke-width',1).attr('stroke-dasharray','4 3')
  .style('pointer-events','none').style('visibility','hidden');
 
// Mouse overlay
svg.style('cursor','crosshair')
  .on('mousemove', function(event){{
    const [rawX, rawY] = d3.pointer(event, g.node());
    const mx = rawX;
    if(mx < 0 || mx > VW) return;
    const [mx] = d3.pointer(event);
    const yr = xSc.invert(mx);
    const snap = years.reduce((a,b)=>Math.abs(b-yr)<Math.abs(a-yr)?b:a);
    lastSnap = snap;
 
    // Position tooltip using % of SVG container width (works in iframe)
    const svgNode = document.getElementById('chart');
    const svgW = svgNode.clientWidth || svgNode.getBoundingClientRect().width || 600;
    const scale = svgW / TOTAL_W;  // pixels per viewBox unit
 
    const rulePixelX = (mx + ML) * scale; // pixel x of the rule in the container
    const ttW = 220;
    const ttH = 220;
    const wrapH = svgNode.clientHeight || svgNode.getBoundingClientRect().height || 300;
 
    // Flip tooltip to left of rule if it would overflow right
    let left = rulePixelX + 10;
    if (left + ttW > svgW - 5) left = rulePixelX - ttW - 10;
    left = Math.max(2, left);
 
    // Vertically centre in the chart area
    const chartTopPx = MT * scale;
    const chartHPx   = VH * scale;
    let top = chartTopPx + chartHPx/2 - ttH/2;
    top = Math.max(2, top);
 
    const tt = document.getElementById('tooltip');
    tt.style.left  = left + 'px';
    tt.style.top   = top  + 'px';
    tt.style.display = 'block';
 
    showTooltip(snap);
  }})
  .on('mouseleave',()=>{{
    rule.style('visibility','hidden');
    dotsG.selectAll('*').remove();
    document.getElementById('tooltip').style.display='none';
  }});
 
function render(ind){{
  const data=getByRegion(ind);
  const allV=Object.values(data).flatMap(r=>Object.values(r));
  const [vmin,vmax]=d3.extent(allV);
  const pad=(vmax-vmin)*0.12;
  ySc.domain([Math.max(0,vmin-pad),vmax+pad]);
 
  xAxisG.call(d3.axisBottom(xSc).tickFormat(d3.format('d')).ticks(8))
    .selectAll('text').style('fill','#898781').style('font-size','11px');
  xAxisG.select('.domain').style('stroke','#e1e0d9');
  xAxisG.selectAll('.tick line').style('stroke','#e1e0d9');
 
  yAxisG.call(d3.axisLeft(ySc).ticks(5).tickFormat(d=>d+'%'))
    .selectAll('text').style('fill','#898781').style('font-size','11px');
  yAxisG.select('.domain').style('stroke','none');
  yAxisG.selectAll('.tick line').style('stroke','none');
 
  gridG.selectAll('line').remove();
  ySc.ticks(5).forEach(t=>{{
    gridG.append('line')
      .attr('x1',0).attr('x2',VW).attr('y1',ySc(t)).attr('y2',ySc(t))
      .attr('stroke','#e8e8e8').attr('stroke-width',0.8);
  }});
 
  const line=d3.line()
    .x(d=>xSc(d[0])).y(d=>ySc(d[1]))
    .defined(d=>d[1]!=null)
    .curve(d3.curveCatmullRom.alpha(0.5));
 
  linesG.selectAll('*').remove();
  labelsG.selectAll('*').remove();
  dotsG.selectAll('*').remove();
 
  regions.filter(r=>r!=='MENA').concat(['MENA']).forEach(region=>{{
    const pts=years.filter(y=>data[region]&&data[region][y]!=null).map(y=>[y,data[region][y]]);
    if(!pts.length)return;
    const isMena=region==='MENA';
    linesG.append('path').datum(pts)
      .attr('fill','none')
      .attr('stroke',isMena?COLORS['MENA']:(MUTED[region]||'#ccc'))
      .attr('stroke-width',isMena?3.5:1.3)
      .attr('opacity',isMena?1:0.65)
      .attr('d',line);
    if(isMena){{
      const last=pts[pts.length-1];
      labelsG.append('text')
        .attr('x',xSc(last[0])+7).attr('y',ySc(last[1])+4)
        .attr('fill',COLORS['MENA']).attr('font-size','12px').attr('font-weight','700')
        .text('MENA');
    }}
  }});
}}
 
function showTooltip(snap){{
  const data=getByRegion(currentInd);
  rule.attr('x1',xSc(snap)).attr('x2',xSc(snap)).style('visibility','visible');
 
  // Dots on each line
  dotsG.selectAll('*').remove();
  regions.forEach(r=>{{
    if(data[r]&&data[r][snap]!=null){{
      const isMena=r==='MENA';
      dotsG.append('circle')
        .attr('cx',xSc(snap)).attr('cy',ySc(data[r][snap]))
        .attr('r',isMena?5.5:4)
        .attr('fill',isMena?COLORS['MENA']:(MUTED[r]||'#ccc'))
        .attr('stroke','#fff').attr('stroke-width',1.5);
    }}
  }});
 
  const rows=regions
    .filter(r=>data[r]&&data[r][snap]!=null)
    .map(r=>({{region:r,val:data[r][snap]}}))
    .sort((a,b)=>b.val-a.val);
 
  document.getElementById('ttYear').textContent=snap;
  document.getElementById('ttRows').innerHTML=rows.map(r=>{{
    const isMena=r.region==='MENA';
    const color=isMena?COLORS['MENA']:'#52514e';
    const bg=isMena?'rgba(29,158,117,0.09)':'transparent';
    const dot=isMena?COLORS['MENA']:(MUTED[r.region]||'#ccc');
    const weight=isMena?'700':'400';
    return `<div class="tt-row" style="background:${{bg}}">
      <div class="tt-left">
        <div class="tt-dot" style="background:${{dot}}"></div>
        <span class="tt-name" style="color:${{color}};font-weight:${{weight}}">${{r.region}}</span>
      </div>
      <span class="tt-val" style="color:${{color}}">${{r.val.toFixed(1)}}</span>
    </div>`;
  }}).join('');
}}
 
// Legend
const legEl=document.getElementById('legend');
regions.forEach(r=>{{
  const isMena=r==='MENA';
  const item=document.createElement('div');
  item.className='leg-item';
  item.innerHTML=`
    <div style="width:${{isMena?22:14}}px;height:${{isMena?3.5:1.5}}px;background:${{isMena?COLORS[r]:(MUTED[r]||'#ccc')}};border-radius:2px"></div>
    <span style="font-weight:${{isMena?'700':'400'}};color:${{isMena?'#0b0b0b':'#898781'}}">${{r}}</span>`;
  legEl.appendChild(item);
}});
 
render('Blood Pressure');
 
document.getElementById('indicatorSel').addEventListener('change',function(){{
  currentInd=this.value;
  render(this.value);
  // Re-show tooltip at last hovered year if tooltip is visible
  if(document.getElementById('tooltip').style.display==='block') showTooltip(lastSnap);
}});
</script>
</body>
</html>"""
 
with open("global_trend_chart.html","w", encoding="utf-8") as f:
    f.write(html)
print("✅ Written: global_trend_chart.html")