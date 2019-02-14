import React, { Component } from 'react';
import ReactTMI from 'react-tmi';
import axios from 'axios';
import Queue from './Queue.js';

import BarChartComponent from "./BarChartComponent";

class TwitchIRC extends Component {
  constructor() {
    super();
    this.state = {
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
    /** reset messagesAnalyze and data **/
    this.resetChartData = false;
    /** Binding method **/
    this.onMessageHandler = this.onMessageHandler.bind(this);
  };

  componentDidMount() {
    if (this.myClient === null) {

      this.chartDataSelect = this.props.chartDataSelect;
      this.resetChartData = this.props.resetChartData;
      this.channel = `#${this.props.twitchIRCProps.channels[0]}`;

      // create instance
      this.myClient = new ReactTMI.client(this.props.twitchIRCProps);
      // Register our event handlers (defined below)
      this.myClient.on('message', this.onMessageHandler);
      // Connect to server
      this.myClient.connect();

      this.initMessagesAnalyze();
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
    }
    // 更新圖表資料的呈現類型
    if (this.props.chartDataSelect !== this.chartDataSelect) {
        this.chartDataSelect = this.props.chartDataSelect;
        
        if (this.messagesAnalyze[this.chartDataSelect][0] && 
            this.messagesAnalyze[this.chartDataSelect][0].values.length !== 0) {
            let temp = [];
            let objTemp = {};
            objTemp["values"] = this.messagesAnalyze[this.chartDataSelect][0].values.slice(0, 10);
            temp.push(objTemp);
            this.setState({data: temp});
        } else {
            this.initBarChartData();
        }
    }
    // 初始化所有的messageAnalyz data
    if (this.props.resetChartData !== this.resetChartData) {
        this.resetChartData = this.props.resetChartData;
        this.initMessagesAnalyze()
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
    item["x"] = "無資料";
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
    const messageObj = {
      badges: context["badges-raw"],
      badgeObj: context.badges,
      display_name: context["display-name"],
      username: context.username,
      user_id: context["user-id"],
      room_id: context["room-id"],
      tmi_sent_ts: context["tmi-sent-ts"],
      message: msg.trim(),
      keywords: [],
    };

    if (!window.localStorage.getItem(messageObj["room_id"])) {
      this.props.updateRoomID(messageObj["room_id"]);
    };

    if ( this.props.isAuthenticated && this.props.enableLexicalAnalyzeService ) {
        this.state.messagesQueue.enqueue(messageObj);
    }

    // If the command is known, let's execute it
    if (messageObj.message === this.state.singleCommand) {
      const num = this.rollDice();
      /** chat bot say something **/
      this.myClient.say(target, `${num}`);
    }

    if ( this.props.isAuthenticated && this.props.enableLexicalAnalyzeService ) {
        if ( this.state.messagesQueue.getLength() >= this.state.messagesQueueMax ) {
            this.makeLexicalAnalyzeService();
        }
    }
  }

  makeLexicalAnalyzeService() {

    let messages = [];
    let messagesObj = [];

    for ( var i = 0; i <= this.state.messagesQueueMax - 1; i++) {
        let messageObj = this.state.messagesQueue.dequeue();
        messages.push(messageObj.message);
        messagesObj.push(messageObj);
    }

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
        this.updateMessagesAnalyze(JSON.parse(res.data.keywords));
        // update messagesObj's keywords
        if (this.props.enableRepository) {
            let keywordsBySentence = JSON.parse(res.data.keywordsBySentence);
            for (let i=0 ; i < (this.state.messagesQueueMax) ; i++) {
                messagesObj[i].keywords = keywordsBySentence[i]
            }
            this.makeRepositoryService(messagesObj);
        }
    })
  }

  makeRepositoryService(messagesObj) {
    const options = {
        method: 'POST',
        headers: {'Content-Type': 'application/json',
                  'Authorization': `Bearer ${window.localStorage.authToken}`,
                  'LoginType': `${window.localStorage.loginType}`,
        },
        url: `${process.env.REACT_APP_DOMAIN_NAME_URL}/repository/update`,
        data:{sentencesObj: messagesObj}
    };
    axios(options)
    .then((res) => { 
    })
  }

  // Function called when the "dice" command is issued
  rollDice () {
    const sides = 6;
    return Math.floor(Math.random() * sides) + 1;
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
