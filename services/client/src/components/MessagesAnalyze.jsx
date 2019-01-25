import React, { Component } from 'react';

class MessagesAnalyze extends Component {

  get messagesAnalyzeShow() {
    return (
      <ul>
        {this.props.messagesAnalyze.nouns && this.props.messagesAnalyze.nouns.map(term => (
          <li key={term.id}>
            <p>{term.name}:{term.count}</p>
          </li>
        ))}
      </ul>
    );
  }

  messagesAnalyze_() {
    for (let key in this.props.messagesAnalyze) {
      if (this.props.messagesAnalyze.hasOwnProperty(key)) {
        this.messagesAnalyzeShow(key);
      }
    }
  }

  render() {
    return (
        <div>
            { this.messagesAnalyzeShow }
        </div>
    )
  }
}

export default MessagesAnalyze;
