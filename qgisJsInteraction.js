<script type="text/javascript">

    var basket = [];

    var divs = document.querySelectorAll('div.plotly-graph-div');
    [].forEach.call(divs, function(div) {
        var id = div.id;
        div.on('plotly_click', function(data){
            toggleSelection(div,data);
        });
    });

    function sendData(action, a){
        console.log( a);
        var ajson = convertToJson(a);
        if( typeof(plotWebView) != 'undefined' )
            plotWebView.processData( action, ajson );
        //document.getElementById('dataPlotLog').innerHTML = ajson;
    }

    function convertToJson(data){
        return JSON.stringify(data);
    }

    function convertToObject(json) {
        return JSON.parse( json );
    }

    function toggleSelection(div,data){

        var pts = '';
        var pprop = {}
        if( div.data.length ){
            pdata = div.data[0];
            for(var a in pdata){
                if( a != 'x' && a != 'y' && a != 'z' && a != 'labels' && a != 'values' ){
                    pprop[a] = pdata[a];
                }
            }

        }

        for(var i=0; i < data.points.length; i++){
            var d = data.points[i];
            if( 'x' in d ){
                var ret = { 'x': d.x, 'y':d.y, 'properties': pprop };
            }
            if( 'label' in d){
                var ret = { 'label': d.label, 'value':d.v, 'properties': pprop };
            }

            // Action with corresponding filtered QGIS features by expression
            var sel = document.getElementById('dataPlotAction');
            var actionVal = sel.value;
            action = 'select';
            if( actionVal )
                action = actionVal;
            sendData(action, ret);

        }
    }
</script>
