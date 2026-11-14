if (P.target === 'active' && !app.documents.length) throw new Error('No active document');
var scene=P.scene, d=P.target==='new' ? app.documents.add(DocumentColorSpace.RGB,scene.width,scene.height) : app.activeDocument;
if(P.target==='active' && d.name!==P.expected_document) throw new Error('Active document changed; inspect again');
var ab=d.artboards[d.artboards.getActiveArtboardIndex()].artboardRect;
var prefix='SCI_COMPONENTS:'+scene.scene_id, old=null, hits=0;
for(var i=0;i<d.layers.length;i++)if(d.layers[i].name===prefix){old=d.layers[i];hits++;}
if(hits>1)throw new Error('Duplicate scene layers; resolve manually');
if(old && (old.locked || !old.visible))throw new Error('Existing scene layer must be visible and unlocked');
var previousLayer=d.activeLayer, selection=d.selection, stage=null;
var counts={cells:0,nodes:0,edges:0,feature_cells:0,texts:0,arrows:0}, warnings=[], groups={};
function rgb(s){var c=new RGBColor();c.red=parseInt(s.substr(1,2),16);c.green=parseInt(s.substr(3,2),16);c.blue=parseInt(s.substr(5,2),16);return c;}
function path(g,pts,col,w){var p=g.pathItems.add(),q=[];for(var j=0;j<pts.length;j++)q.push([ab[0]+pts[j][0],ab[1]-pts[j][1]]);p.setEntirePath(q);p.filled=false;p.stroked=true;p.strokeColor=rgb(col);p.strokeWidth=w;return p;}
function rect(g,x,y,w,h,col,kind){var p=g.pathItems.rectangle(ab[1]-y,ab[0]+x,w,h);p.filled=true;p.fillColor=rgb(col);p.stroked=true;p.strokeColor=rgb('#FFFFFF');p.strokeWidth=0.5;p.name=kind;counts[kind]++;return p;}
function text(g,s,x,y,c,rotation){if(!s)return;var t=g.textFrames.add();t.contents=s;t.name='text:'+s;try{t.textRange.characterAttributes.textFont=app.textFonts.getByName(c.font);}catch(e){warnings.push('Font fallback: '+c.font);}t.textRange.characterAttributes.size=c.font_size;t.textRange.characterAttributes.fillColor=rgb('#202020');t.textRange.paragraphAttributes.justification=Justification.CENTER;if(rotation)t.rotate(rotation);t.left=ab[0]+x-t.width/2;t.top=ab[1]-y+t.height/2;if(t.contents!==s)throw new Error('Text verification failed');counts.texts++;}
function strip(g,colors,x,y,size){for(var k=0;k<colors.length;k++)rect(g,x+k*size,y,size,size,colors[k],'feature_cells');}
try{
 stage=d.layers.add();stage.name='__building_'+prefix;var artwork=stage.groupItems.add();artwork.name='Scene artwork';
 for(var i=0;i<scene.components.length;i++){
  var c=scene.components[i],g=artwork.groupItems.add();g.name='component:'+c.id;groups[c.id]=g;
  if(c.type==='matrix'){
   for(var r=0;r<c.cells.length;r++)for(var col=0;col<c.cells[r].length;col++)rect(g,c.x+col*c.cell_size,c.y+r*c.cell_size,c.cell_size,c.cell_size,c.cells[r][col],'cells');
   var w=c.cells[0].length*c.cell_size,h=c.cells.length*c.cell_size;
   text(g,c.title,c.x+w/2,c.y-32,c);text(g,c.column_label,c.x+w/2,c.y-14,c);text(g,c.row_label,c.x-16,c.y+h/2,c,90);
  }else if(c.type==='feature_strip'){
   strip(g,c.features,c.x,c.y,c.cell_size);text(g,c.title,c.x+c.features.length*c.cell_size/2,c.y-16,c);
  }else if(c.type==='text')text(g,c.title,c.x,c.y,c);
  else{
   var nodes={};for(var n=0;n<c.nodes.length;n++)nodes[c.nodes[n].id]=c.nodes[n];
   for(var e=0;e<c.edges.length;e++){var edge=c.edges[e],a=nodes[edge.source],b=nodes[edge.target];var p=path(g,[[c.x+a.x,c.y+a.y],[c.x+b.x,c.y+b.y]],edge.color,1);p.name='edge:'+edge.source+'->'+edge.target;counts.edges++;}
   for(var n=0;n<c.nodes.length;n++){var v=c.nodes[n],rad=c.node_radius,p=g.pathItems.ellipse(ab[1]-c.y-v.y+rad,ab[0]+c.x+v.x-rad,rad*2,rad*2);p.filled=true;p.fillColor=rgb('#F8F8F5');p.stroked=true;p.strokeColor=rgb('#303030');p.strokeWidth=1;p.name='node:'+v.id;counts.nodes++;if(v.features.length)strip(g,v.features,c.x+v.x-v.features.length*3,c.y+v.y-rad-10,6);text(g,v.label,c.x+v.x,c.y+v.y+rad+10,c);}
   text(g,c.title,c.x,c.y-32,c);
  }
 }
 var arrows=artwork.groupItems.add();arrows.name='Data flow';
 for(var i=0;i<scene.links.length;i++){
  var l=scene.links[i],a=groups[l.source].visibleBounds,b=groups[l.target].visibleBounds;
  var ac=[(a[0]+a[2])/2,(a[1]+a[3])/2],bc=[(b[0]+b[2])/2,(b[1]+b[3])/2];
  var dx=bc[0]-ac[0],dy=bc[1]-ac[1];if(dx===0&&dy===0)throw new Error('Coincident connected components');
  function boundary(bounds,center,vx,vy){var t=Math.min(vx===0?1e20:(bounds[2]-bounds[0])/2/Math.abs(vx),vy===0?1e20:(bounds[1]-bounds[3])/2/Math.abs(vy));return [center[0]+vx*t,center[1]+vy*t];}
  var start=boundary(a,ac,dx,dy),end=boundary(b,bc,-dx,-dy),len=Math.sqrt(dx*dx+dy*dy),ux=dx/len,uy=dy/len;
  start=[start[0]+ux*5,start[1]+uy*5];end=[end[0]-ux*5,end[1]-uy*5];
  if((end[0]-start[0])*ux+(end[1]-start[1])*uy<8)throw new Error('Connected components overlap or have insufficient gap');
  var ag=arrows.groupItems.add();ag.name='link:'+l.id;
  var p=ag.pathItems.add();p.setEntirePath([start,end]);p.filled=false;p.stroked=true;p.strokeColor=rgb('#555555');p.strokeWidth=1;
  var h=ag.pathItems.add();h.setEntirePath([end,[end[0]-6*ux+2.5*uy,end[1]-6*uy-2.5*ux],[end[0]-6*ux-2.5*uy,end[1]-6*uy+2.5*ux]]);h.closed=true;h.filled=true;h.fillColor=rgb('#555555');h.stroked=false;counts.arrows++;
  text(ag,l.label,(start[0]+end[0])/2-ab[0],ab[1]-(start[1]+end[1])/2-12,{font:'ArialMT',font_size:10});
 }
 for(var key in P.expected)if(counts[key]!==P.expected[key])throw new Error('Count mismatch: '+key);
 var bounds=artwork.visibleBounds;
 if(bounds[0]<ab[0]||bounds[1]>ab[1]||bounds[2]>ab[2]||bounds[3]<ab[3])warnings.push('Artwork extends beyond active artboard');
 // Commit only after the full replacement has been built and verified.
 stage.name=prefix;if(old)old.remove();
}catch(error){if(stage)stage.remove();try{d.activeLayer=previousLayer;d.selection=selection;}catch(ignore){}throw new Error(String(error)+' original line='+error.line);}
try{if(previousLayer!==old)d.activeLayer=previousLayer;d.selection=selection;}catch(ignore){}
app.redraw();
return sciJSON({document:d.name,scene_id:scene.scene_id,counts:counts,warnings:warnings,layer:prefix});
