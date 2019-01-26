import React, { Component }  from "react";
import { BarChart } from "react-d3-components";

class BarChartComponent extends Component {

  // when curser on the bar, it will show the y value
  tooltip(x, y0, y, total) {
    return y.toString();
  };

  render() {
      return (
        <BarChart
          data={this.props.data}
          width={800}
          height={200}
          tooltipHtml={this.tooltip} 
          margin={{ top: 10, bottom: 50, left: 50, right: 10 }}
          colorByLabel={false} // different color for each bar
          xAxis={{innerTickSize: 6, label: "關鍵字"}}
          yAxis={{label: "次數"}}
        />
      );
  }
}

export default BarChartComponent;
