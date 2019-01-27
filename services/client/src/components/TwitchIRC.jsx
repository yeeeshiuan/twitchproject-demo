import React, { Component } from 'react';
import ReactTMI from 'react-tmi';
import axios from 'axios';
import Queue from './Queue.js';

import BarChartComponent from "./BarChartComponent";

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
      data: [],
    };
    /** channel **/
    this.channel = "";
    /** chart data select status **/
    this.chartDataSelect= "";
    /** messages data analyze from lexical service **/
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

      this.chartDataSelect = this.props.chartDataSelect;

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

  componentDidUpdate() {
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

      // messagesQueue and data reset
      this.setState({messagesQueue: new Queue(),
                     data: []});

      this.initMessagesAnalyze();

      console.log("2");
      console.log(this.props.twitchIRCProps.channels[0]);
      console.log(this.channel);
    }
    // 更新圖表資料的呈現類型
    if (this.props.chartDataSelect !== this.chartDataSelect) {
        this.chartDataSelect = this.props.chartDataSelect;
        
        if (this.messagesAnalyze[this.chartDataSelect][0] && 
            this.messagesAnalyze[this.chartDataSelect][0].values.length !== 0) {
            console.log(this.messagesAnalyze[this.chartDataSelect][0].values.length);
            let temp = [];
            let objTemp = {};
            objTemp["values"] = this.messagesAnalyze[this.chartDataSelect][0].values.slice(0, 10);
            temp.push(objTemp);
            this.setState({data: temp});
        } else {
            this.initBarChartData();
        }
    }
  }

  initMessagesAnalyze() {
    this.messagesAnalyze.nouns = [];
    this.messagesAnalyze.verbs = [];
    this.messagesAnalyze.adjs = [];

    this.initBarChartData();
  }

  initBarChartData() {
    // 初始化要餵給bar chart 的資料
    let data = []
    let obj = {};
    obj["values"] = [];
    let item = {};
    item["x"] = "初始化中";
    item["y"] = 0;
    obj.values.push(item);
    data.push(obj);
    this.setState({data: data});
  }

  updateMessagesAnalyze(resMessages) {
    for (let key in this.messagesAnalyze) {
      if (this.messagesAnalyze.hasOwnProperty(key)) {
        this.updateObject(key, resMessages[key]);
      }
    }
  }

  updateObject(tag, sourceObject) {
    // if exist then update, if not exist then add

    let valueObj = this.messagesAnalyze[tag][0] || {};
    if ( !valueObj.values ) {
        valueObj["values"] = [];
    }

    for (let key in sourceObject) {
        // skip loop if the property is from prototype
        if (!sourceObject.hasOwnProperty(key)) continue;

        let obj = {};
        let findIndex = valueObj.values.findIndex( cell => {
                                return cell.x === key
                        });
        if ( findIndex === -1 ) {
            obj["x"] = key;
            obj["y"] = sourceObject[key];
            valueObj.values.push(obj);
        } else {
            valueObj.values[findIndex].y += sourceObject[key];
        }
    }
    if (this.messagesAnalyze[tag][0]) {
        this.messagesAnalyze[tag].pop();
    }
    this.messagesAnalyze[tag].push(valueObj);

    // sort by count descending
    this.messagesAnalyze[tag][0].values.sort((a, b) => parseFloat(b.y) - parseFloat(a.y));

    // test
    if ( tag === this.props.chartDataSelect ) {
        if ( this.messagesAnalyze[tag][0] && 
             this.messagesAnalyze[tag][0].values.length !== 0 ) {
            let arrayTemp = [];
            let objTemp = {};
            objTemp["values"] = this.messagesAnalyze[tag][0].values.slice(0, 10);
            arrayTemp.push(objTemp);
            this.setState({data: arrayTemp});
        } else {
            this.initBarChartData();
        }

    }

  }

  // Called every time a message comes in
  onMessageHandler (target, context, msg, self) {
    //if (self) { return; } // Ignore messages from the bot

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
        console.log(res.data.message);
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

  messagesLoop() {
    return Object.keys(this.messagesAnalyze);
  }

  get messagesBarChart() {

    let keyArray = this.messagesLoop();
    console.log(keyArray);
    console.log(typeof keyArray);
    let messagesObject = this.messagesAnalyze;
    if ( this.props.isAuthenticated && this.props.enableLexicalAnalyzeService ) {
        return (
          <div>
                { keyArray && keyArray.map(key => (
                    <BarChartComponent data={messagesObject[key]}/>
                )) }
          </div>
        );
    } else {
        return (
            <p>messagesBarChart</p>
        );
    }
  }

  render() {
    return (
        <div>
            { this.state.data[0] && this.state.data[0].values.length !== 0 &&
            <BarChartComponent data={this.state.data}/>
            }
        </div>
    )
  }
}

export default TwitchIRC;
