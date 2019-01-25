import React, { Component } from 'react';
import ReactTMI from 'react-tmi';
import axios from 'axios';
import Queue from './Queue.js';

import MessageList from './MessageList';

class TwitchIRC extends Component {
  constructor() {
    super();
    this.state = {
      /** messages **/
      messages:[],
      messageCount: 0,
      messageCountMax: 5,
      /** custom commands **/
      singleCommand: '!7777',
      /** messages queue **/
      messagesQueue: new Queue(),
      /** max messages queue has **/
      messagesQueueMax: 10,
    };
    /** channel **/
    this.channel = "";
    /**  **/
    this.messagesAnalyze = {};
    /** My TMI client */
    this.myClient = null;

    /** Binding method **/
    this.onMessageHandler = this.onMessageHandler.bind(this);

  };

  componentDidMount() {
    if (this.myClient === null) {
      //debug
      console.log(this.props.twitchIRCProps);

      this.channel = `#${this.props.twitchIRCProps.channels[0]}`;

      // create instance
      this.myClient = new ReactTMI.client(this.props.twitchIRCProps);

      // Register our event handlers (defined below)
      this.myClient.on('message', this.onMessageHandler);

      // Connect to server
      this.myClient.connect();

      // debug
      console.log(this.myClient);

      this.initMessagesAnalyze();
      console.log("1");
      console.log(this.props.twitchIRCProps.channels[0]);
      console.log(this.channel);
    }
  };


  componentWillUpdate() {
    // You don't have to do this check first, but it can help prevent an unneeded render
    if (this.props.twitchIRCProps.channels[0] !== this.channel) {
      this.channel =  `#${this.props.twitchIRCProps.channels[0]}`;

      this.myClient.disconnect();

      // create instance
      this.myClient = new ReactTMI.client(this.props.twitchIRCProps);

      // Register our event handlers (defined below)
      this.myClient.on('message', this.onMessageHandler);

      // Connect to server
      this.myClient.connect();

      // messagesQueue reset
      this.setState({messagesQueue: new Queue()});

      this.initMessagesAnalyze();

      console.log("2");
      console.log(this.props.twitchIRCProps.channels[0]);
      console.log(this.channel);
    }
  }

  initMessagesAnalyze() {
    this.messagesAnalyze.nouns = [];
    this.messagesAnalyze.verbs = [];
    this.messagesAnalyze.adjs = [];
  }

  updateMessagesAnalyze(resMessages) {
    for (let key in this.messagesAnalyze) {
      if (this.messagesAnalyze.hasOwnProperty(key)) {
        this.updateObject(key, resMessages[key]);
      }
    }
  }

  updateObject(tag, sourceObject) {
    
    for (let key in sourceObject) {
        // skip loop if the property is from prototype
        if (!sourceObject.hasOwnProperty(key)) continue;

        let obj = {};
        let findIndex = this.messagesAnalyze[tag].findIndex( cell => {
                            return cell.name === key
                        });

        if ( findIndex === -1 ) {
            obj["name"] = key;
            obj["count"] = sourceObject[key];
            obj["id"] = 0;
            this.messagesAnalyze[tag].push(obj);
        } else {
            this.messagesAnalyze[tag][findIndex].count += sourceObject[key];
        }
    }
    // give every cell a id
    let id = 0;
    for (let index in this.messagesAnalyze[tag]) {
        // skip loop if the property is from prototype
        if (!this.messagesAnalyze[tag].hasOwnProperty(index)) continue;
        
        this.messagesAnalyze[tag][index].id = id
        id = id + 1;
    }
    // sort by count descending
    this.messagesAnalyze[tag].sort((a, b) => parseFloat(b.count) - parseFloat(a.count));

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

    this.state.messagesQueue.enqueue(message.text);

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

    if ( this.props.isAuthenticated && this.props.enableLexicalAnalyzeService ) {
        if ( this.state.messagesQueue.getLength() >= this.state.messagesQueueMax ) {
            this.makeLexicalAnalyzeService();
        }
    }
  }

  makeLexicalAnalyzeService() {

    let messages = [];

    console.log(`Length before: ${this.state.messagesQueue.getLength()}`);

    for ( var i = 0; i <= this.state.messagesQueueMax - 1; i++) {
        messages.push(this.state.messagesQueue.dequeue())
    }

    console.log(`Length after: ${this.state.messagesQueue.getLength()}`);

    const options = {
        method: 'POST',
        headers: {'Content-Type': 'application/json',
                  'Authorization': `Bearer ${window.localStorage.authToken}`,
                  'LoginType': `${window.localStorage.loginType}`,
        },
        url: `${process.env.REACT_APP_DOMAIN_NAME_URL}/lexical/sentences`,
        data:{sentences: messages}
    };
    axios(options)
    .then((res) => { 
        this.updateMessagesAnalyze(JSON.parse(res.data.message));
        console.log(this.messagesAnalyze);
    })
    .catch((error) => { 
        // Error
        if (error.response) {
            // The request was made and the server responded with a status code
            // that falls out of the range of 2xx
            console.log(error.response.data);
            console.log(error.response.status);
            console.log(error.response.headers);
        } else if (error.request) {
            // The request was made but no response was received
            // `error.request` is an instance of XMLHttpRequest in the browser and an instance of
            // http.ClientRequest in node.js
            console.log(error.request);
        } else {
            // Something happened in setting up the request that triggered an Error
            console.log('Error', error.message);
        }
        console.log(error.config);
     });
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
