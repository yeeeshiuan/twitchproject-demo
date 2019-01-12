import React, { Component } from 'react';

class MessageList extends Component {

  render() {
    {console.log("MessageList");}
    return (
        this.props.messages.map(message => {
          return (
           <li key={message.id}>
               {message.text}
           </li>
          )
        })
    )
  }
}

export default MessageList;
