import React, { Component } from 'react';
import ReactTMI from 'react-tmi';
import MessageList from './MessageList';

class TwitchIRC extends Component {
  constructor() {
    super();
    this.state = {
      /** channel **/
      channel:"",
      /** messages **/
      messages:[],
      messageCount: 0,
      messageCountMax: 5,
      /** custom commands **/
      singleCommand: '!7777',
    };
    /** My TMI client */
    this.myClient = null;

    /** Binding method **/
    this.onMessageHandler = this.onMessageHandler.bind(this);

  };

  componentDidMount() {
    if (this.myClient === null) {
      //debug
      console.log(this.props.twitchIRCProps);

      this.setState({channel: this.props.twitchIRCProps.channels[0]});

      // create instance
      this.myClient = new ReactTMI.client(this.props.twitchIRCProps);

      // Register our event handlers (defined below)
      this.myClient.on('message', this.onMessageHandler);

      // Connect to server
      this.myClient.connect();

      // debug
      console.log(this.myClient);
    }
  };


  componentWillReceiveProps() {
    // You don't have to do this check first, but it can help prevent an unneeded render
    if (this.props.twitchIRCProps.channels[0] !== this.state.channel) {
      this.setState({channel: this.props.twitchIRCProps.channels[0]});

      this.myClient.disconnect();

      // create instance
      this.myClient = new ReactTMI.client(this.props.twitchIRCProps);

      // Register our event handlers (defined below)
      this.myClient.on('message', this.onMessageHandler);

      // Connect to server
      this.myClient.connect();
    }
  }

  // Called every time a message comes in
  onMessageHandler (target, context, msg, self) {
    if (self) { return; } // Ignore messages from the bot

    // Remove whitespace from chat message
    const message = {
      id: this.state.messageCount,
      text: msg.trim(),
    };

    let messageCountTmp = this.state.messageCount;
    if (messageCountTmp >= this.state.messageCountMax) {
      messageCountTmp = 0;
    } else {
      messageCountTmp = messageCountTmp + 1;
    }

    let messagesTmp = [...this.state.messages];
    // control the size of messages
    if (messagesTmp.length >= this.state.messageCountMax) {
      // remove older data
      messagesTmp = messagesTmp.slice(1);
    }

    // If the command is known, let's execute it
    if (message.text === this.state.singleCommand) {
      const num = this.rollDice();
      /** chat bot say something **/
      this.myClient.say(target, `${num}`);
      console.log(`* Executed ${message.text} command`);

      /* append new data */
      messagesTmp.push(message);
      this.setState({
          messages: messagesTmp,
          messageCount: messageCountTmp,
      });

    } else {
      console.log(`* Unknown command ${message.text}`);

      /* append new data */
      messagesTmp.push(message);
      this.setState({
          messages: messagesTmp,
          messageCount: messageCountTmp,
      });
    }
  }

  // Function called when the "dice" command is issued
  rollDice () {
    const sides = 6;
    return Math.floor(Math.random() * sides) + 1;
  }

  render() {
    return (
        <MessageList messages={this.state.messages} />
    )
  }
}

export default TwitchIRC;
