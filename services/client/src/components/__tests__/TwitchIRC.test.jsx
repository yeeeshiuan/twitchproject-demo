import React from 'react';
import { shallow, mount } from 'enzyme';
import renderer from 'react-test-renderer';
import Queue from '../Queue.js';
jest.mock('../Queue.js');
import BarChartComponent from "../BarChartComponent";
jest.mock('../BarChartComponent');

import TwitchIRC from '../TwitchIRC';


const twitchIRCProps = {
        options: {
        /** delieve log messages */
            debug: false
        },
        connection: {
            reconnect: true
        },
        identity: {
          username:`${process.env.REACT_APP_TWITCH_USER_NAME}` ,
          password:`${process.env.REACT_APP_TWITCH_OAUTH_TOKEN}`,
        },
        channels: ['test'],
      };

test('TwitchIRC renders without crashing', () => {
  const wrapper = shallow(<TwitchIRC twitchIRCProps={twitchIRCProps}/>);
});

test('TwitchIRC will call componentDidMount when mounted', () => {
  const onDidMount = jest.fn();
  TwitchIRC.prototype.componentDidMount = onDidMount;
  const wrapper = mount(<TwitchIRC/>);
  expect(onDidMount).toHaveBeenCalledTimes(1)
});

test('TwitchIRC will call componentDidUpdate when props update', () => {
  const onDidUpdate = jest.fn();
  TwitchIRC.prototype.componentDidUpdate = onDidUpdate;
  const wrapper = mount(<TwitchIRC twitchIRCProps={twitchIRCProps}/>);
  wrapper.setProps({ twitchIRCProps: {channels: ['testme']} });
  expect(onDidUpdate).toHaveBeenCalledTimes(1)
});

test('TwitchIRC When no data', () => {
  const wrapper = shallow(<TwitchIRC twitchIRCProps={twitchIRCProps}/>);
  wrapper.setState({data: [] });
  const barChartComponent = wrapper.find('BarChartComponent');
  expect(barChartComponent.length).toBe(0);
  const div = wrapper.find('div');
  expect(div.length).toBe(1);
});

test('TwitchIRC When it has data', () => {
  const wrapper = shallow(<TwitchIRC twitchIRCProps={twitchIRCProps}/>);
  wrapper.setState({data: [{values: ['test']}]});
  const barChartComponent = wrapper.find('BarChartComponent');
  expect(barChartComponent.length).toBe(1);
  const div = wrapper.find('div');
  expect(div.length).toBe(1);
});
