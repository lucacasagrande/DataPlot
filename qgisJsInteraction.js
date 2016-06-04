<script type="text/javascript">

    var basket = [];

    var divs = document.querySelectorAll('div.plotly-graph-div');
    [].forEach.call(divs, function(div) {
        var id = div.id;
        div.on('plotly_click', function(data){
            toggleSelection(div,data);
        });
    });

    function logData(a){
        console.log( a);
        var ajson = convertToJson(a);
        if( typeof(plotWebView) != 'undefined' )
            plotWebView.log( convertToJson(a) );
        document.getElementById('dataPlotLog').innerHTML = ajson;
    }

    function convertToJson(data){
        return JSON.stringify(data);
    }

    function convertToObject(json) {
        return JSON.parse( json );
    }

    function toggleSelection(div,data){
        //logData(data);
        var pts = '';
        for(var i=0; i < data.points.length; i++){
            var d = data.points[i];
            if( 'x' in d ){
                var ret = { 'x': d.x, 'y':d.y };
            }
            if( 'label' in d){
                var ret = { 'label': d.label, 'value':d.v }
            }
            logData(ret)

        }
    }
</script>
