import React from 'react';
import { shallow, mount } from 'enzyme';
import { MemoryRouter as Router } from 'react-router-dom';
import renderer from 'react-test-renderer';

import MessageList from '../MessageList';


test('MessageList renders without crashing', () => {
  const findingResult = [];
  const wrapper = shallow(<MessageList findingResult={findingResult} />);
});

test('MessageList renders a snapshot properly', () => {
  const findingResult = [];
  const tree = renderer.create(<MessageList findingResult={findingResult} />).toJSON();
  expect(tree).toMatchSnapshot();
});

test('MessageList When the findingResult is empty.', () => {
  const findingResult = [];
  const wrapper = shallow(<MessageList findingResult={findingResult} />);
  const i = wrapper.find('i');
  expect(i.length).toBe(1);
  expect(i.get(0).props.children).toBe('目前沒有資料。');
});

test('MessageList When the findingResult has data.(display_name)', () => {
  const findingResult = [{display_name: "An user name",
                          id: 0}];
  const wrapper = shallow(<MessageList findingResult={findingResult} />);
  const ul = wrapper.find('ul');
  expect(ul.length).toBe(1);
  const li = ul.find('li');
  expect(li.length).toBe(2);
  expect(li.get(1).props.children).toBe('An user name');
});

test('MessageList When the findingResult has data.(display_name)', () => {
  const findingResult = [{tmi_sent_ts: "1234567890",
                          id: 0,
                          room_id:["number 1"], 
                          message:"5566得第一。"}];
  const wrapper = shallow(<MessageList findingResult={findingResult} />);
  const ul = wrapper.find('ul');
  expect(ul.length).toBe(1);
  const li = ul.find('li');
  expect(li.length).toBe(2);
  let time = new Date(parseInt(findingResult[0].tmi_sent_ts));
  let options = { weekday:'long', 
                  year:   'numeric', 
                  month:  '2-digit', 
                  day:    '2-digit', 
                  hour:   '2-digit', 
                  minute: '2-digit', 
                  second: '2-digit',
                  hour12: false};
  let roomDisplayName = findingResult[0].room_id[0]
  const result = [];
  result.push(roomDisplayName + ' (' + time.toLocaleDateString("zh-TW", options) + ') : ');
  result.push( " ");
  result.push( <br />);
  result.push( " ");
  result.push(findingResult[0].message);
  expect(li.get(1).props.children).toEqual(result);
});
