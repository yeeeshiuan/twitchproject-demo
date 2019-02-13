import React from 'react';
import { shallow, mount } from 'enzyme';
import { MemoryRouter as Router } from 'react-router-dom';

import App from '../../App';


test('App renders without crashing', () => {
  const wrapper = shallow(<App/>);
});

test('App will call componentWillMount when mounted', () => {
  const onWillMount = jest.fn();
  App.prototype.componentWillMount = onWillMount;
  const wrapper = mount(<Router><App/></Router>);
  expect(onWillMount).toHaveBeenCalledTimes(1)
});

test('App will call componentDidMount when mounted', () => {
  const onDidMount = jest.fn();
  App.prototype.componentDidMount = onDidMount;
  const wrapper = mount(<Router><App/></Router>);
  expect(onDidMount).toHaveBeenCalledTimes(1)
});

test('When not authenticated', () => {
  const wrapper = shallow(<App/>);
  const twitchIRCProps = {channels: ['channelName']};
  wrapper.setState({ twitchIRCProps: twitchIRCProps });
  console.log(wrapper.debug());
});
