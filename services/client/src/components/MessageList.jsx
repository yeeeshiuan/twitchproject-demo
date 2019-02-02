import React, { Component } from 'react';

class MessageList extends Component {

  get data() {
    return (this.props.findingResult.map(result => {
              let main = "";
              if (result.display_name) {
                main = result.display_name;
              } else {
                let time = new Date(parseInt(result.tmi_sent_ts));
                let options = { weekday:'long', 
                                year:   'numeric', 
                                month:  '2-digit', 
                                day:    '2-digit', 
                                hour:   '2-digit', 
                                minute: '2-digit', 
                                second: '2-digit',
                                hour12: false};
                main = time.toLocaleDateString("zh-TW", options) + ' : ' + result.message;
                
              }
                  return (
                           <li key={result.id}>
                               {main}
                           </li>
                  )
        }))
  }

  render() {
    const result = this.props.findingResult.length;
    return (
            <div>
            { result > 0 ? (
              <ul>
              <li>筆數： {result}</li>
              {this.data}
              </ul>
            ) : (
              <i>目前沒有資料。</i>
            )}
            </div>
    );
  }
}

export default MessageList;
