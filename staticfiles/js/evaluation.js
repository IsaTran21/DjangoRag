export default function drawChart(element, data, name, useLayout=false){

    let layout = {
            height: 400,
            width: 500,
            title: {
                text: name,
                font: {
                family: 'Arial, sans-serif',
                size: 24,
                color: '#7f7f7f'}
            }
        }

    if (name && !useLayout){
        Plotly.newPlot(element, data, layout);
        }
    else if (useLayout){

        let combinedLayout = { ...layout, ...useLayout }; // The title from the useLayout will overwrite the layout
        combinedLayout["title"]["font"] = {
                family: 'Arial, sans-serif',
                size: 24,
                color: '#7f7f7f'}
        console.log("this is the combinedLayout", combinedLayout);
        Plotly.newPlot(element, data, combinedLayout);
    }
    else {
        console.log("argument passing issues")
    }
    
};


// let data2 = [{
//         values: [19, 26, 55],
//         labels: ['Residential', 'Non-Residential', 'Utility'],
//         type: 'pie',
//         }];
// pieChart(data2);
