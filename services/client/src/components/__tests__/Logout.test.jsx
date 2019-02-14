import React from 'react';
import { shallow, mount } from 'enzyme';
import { MemoryRouter as Router } from 'react-router-dom';

import Logout from '../Logout';


test('Logout renders without crashing', () => {
  const logoutUser = jest.fn();
  const wrapper = shallow(<Logout  logoutUser={logoutUser}/>);
  expect(logoutUser).toHaveBeenCalledTimes(1)
});

test('Logout will call componentDidMount when mounted', () => {
  const onDidMount = jest.fn();
  Logout.prototype.componentDidMount = onDidMount;
  const wrapper = mount(<Router><Logout/></Router>);
  expect(onDidMount).toHaveBeenCalledTimes(1)
});
