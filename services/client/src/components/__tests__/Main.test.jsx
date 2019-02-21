import React from 'react';
import { shallow, mount } from 'enzyme';
import { MemoryRouter as Router } from 'react-router-dom';

import Main from '../Main';


test('Main renders without crashing', () => {
  const wrapper = shallow(<Main/>);
});

test('Main will call componentDidMount when mounted', () => {
  const onDidMount = jest.fn();
  Main.prototype.componentDidMount = onDidMount;
  const wrapper = mount(<Router><Main/></Router>);
  expect(onDidMount).toHaveBeenCalledTimes(1)
});

test('Main When not authenticated', () => {
  const wrapper = shallow(<Main isAuthenticated={false} 
                                enableRepository={true}
                                enableLexicalAnalyzeService={true} />);
  const twitchIRCProps = {channels: ['channelName']};
  wrapper.setState({twitchIRCProps: twitchIRCProps});

  const form = wrapper.find('form');
  expect(form.length).toBe(1);
  const label = form.find('label');
  expect(label.length).toBe(1);
  expect(label.get(0).props.children).toBe('頻道ID');
  const input = form.find('input');
  expect(input.length).toBe(2);
  expect(input.get(0).props.name).toBe('channelName');
  expect(input.get(1).props.value).toBe('換頻道');

  const twitchEmbedVideo = wrapper.find('TwitchEmbedVideo');
  expect(twitchEmbedVideo.length).toBe(1);
  expect(twitchEmbedVideo.get(0).props.targetClass).toBe('twitch-embed');

  const twitchIRC = wrapper.find('TwitchIRC');
  expect(twitchIRC.length).toBe(1);
  expect(twitchIRC.get(0).props.isAuthenticated).toBe(false);

  const messageList = wrapper.find('MessageList');
  expect(messageList.length).toBe(1);
});

test('Main When authenticated', () => {
  const wrapper = shallow(<Main isAuthenticated={true}
                                enableRepository={true}
                                enableLexicalAnalyzeService={true} />);
  const twitchIRCProps = {channels: ['channelName']};
  wrapper.setState({twitchIRCProps: twitchIRCProps});

  const form = wrapper.find('form');
  expect(form.length).toBe(5);
  const label = form.find('label');
  expect(label.length).toBe(5);
  expect(label.get(0).props.children).toBe('頻道ID');
  expect(label.get(1).props.children).toBe('用ID找發言');
  expect(label.get(2).props.children).toBe('用名稱找發言');
  expect(label.get(3).props.children).toBe('用分詞找發言人名稱');
  expect(label.get(4).props.children).toBe('用完整的句子找發言人名稱');
  const input = form.find('input');
  expect(input.length).toBe(10);
  expect(input.get(0).props.name).toBe('channelName');
  expect(input.get(1).props.value).toBe('換頻道');
  expect(input.get(2).props.name).toBe('findSentencesByUsername');
  expect(input.get(3).props.value).toBe('尋找');
  expect(input.get(4).props.name).toBe('findSentencesByDisplay_name');
  expect(input.get(5).props.value).toBe('尋找');
  expect(input.get(6).props.name).toBe('findDisplay_namesByKeyword');
  expect(input.get(7).props.value).toBe('尋找');
  expect(input.get(8).props.name).toBe('findDisplay_namesBySentence');
  expect(input.get(9).props.value).toBe('尋找');

  const g_label = wrapper.find('label');
  expect(g_label.length).toBe(10);
  const g_input = wrapper.find('input');
  expect(g_input.length).toBe(13);

  const twitchEmbedVideo = wrapper.find('TwitchEmbedVideo');
  expect(twitchEmbedVideo.length).toBe(1);
  expect(twitchEmbedVideo.get(0).props.targetClass).toBe('twitch-embed');

  const twitchIRC = wrapper.find('TwitchIRC');
  expect(twitchIRC.length).toBe(1);
  expect(twitchIRC.get(0).props.isAuthenticated).toBe(true);

  const messageList = wrapper.find('MessageList');
  expect(messageList.length).toBe(1);

});
