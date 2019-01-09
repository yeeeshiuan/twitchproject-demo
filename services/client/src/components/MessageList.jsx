import React, { Component } from 'react';

class MessageList extends Component {
  constructor() {
    super();
  }

  render() {
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
