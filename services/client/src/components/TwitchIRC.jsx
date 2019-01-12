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

      //debug
      console.log(this.props.twitchIRCProps);

      this.myClient.disconnect();

      // create instance
      this.myClient = new ReactTMI.client(this.props.twitchIRCProps);

      // Register our event handlers (defined below)
      this.myClient.on('message', this.onMessageHandler);

      // Connect to server
      this.myClient.connect();

      // debug
      console.log(this.myClient);
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

    if (this.state.messageCount >= 5) {
      this.setState({
          messageCount: 0,
      });
    } else {
      this.setState({
          messageCount: this.state.messageCount + 1,
      });
    }
    console.log(this.state.messageCount);

    // control the size of messages
    if (this.state.messages.length >= 5) {
      this.setState({
        messages: [...this.state.messages.slice(1)],
      });
    }

    // If the command is known, let's execute it
    if (message.text === '!7777') {
      const num = this.rollDice();
      this.myClient.say(target, `${num}`);
      console.log(`* Executed ${message.text} command`);
      
      this.setState({
          messages: this.state.messages.concat(message),
      });

    } else {
      console.log(`* Unknown command ${message.text}`);

      this.setState({
          messages: this.state.messages.concat(message),
      });
    }
  }

  // Function called when the "dice" command is issued
  rollDice () {
    const sides = 6;
    return Math.floor(Math.random() * sides) + 1;
  }

  render() {
    {console.log(this.state.channel);}
    return (
        <MessageList messages={this.state.messages} />
    );
  }
}

export default TwitchIRC;
