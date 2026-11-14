// ExtendScript does not provide JSON in every Illustrator session.
function sciJSON(value) {
    if(value===null)return 'null';
    if(typeof value==='string')return '"'+value.replace(/[\x00-\x1f\\"]/g,function(c){var h=c.charCodeAt(0).toString(16);return '\\u'+('0000'+h).slice(-4);})+'"';
    if(typeof value==='number'||typeof value==='boolean')return String(value);
    var parts=[],i;
    if(value instanceof Array){for(i=0;i<value.length;i++)parts.push(sciJSON(value[i]));return '['+parts.join(',')+']';}
    for(i in value)if(value.hasOwnProperty(i))parts.push(sciJSON(i)+':'+sciJSON(value[i]));
    return '{'+parts.join(',')+'}';
}
