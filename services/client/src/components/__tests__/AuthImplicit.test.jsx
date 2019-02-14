import React from 'react';
import { shallow, mount } from 'enzyme';
import { MemoryRouter as Router } from 'react-router-dom';

import AuthImplicit from '../AuthImplicit';


test('AuthImplicit renders without crashing', () => {
  const wrapper = shallow(<Router><AuthImplicit/></Router>);
});

test('AuthImplicit will call componentDidMount when mounted', () => {
  const onDidMount = jest.fn();
  AuthImplicit.prototype.componentDidMount = onDidMount;
  const wrapper = mount(<Router><AuthImplicit/></Router>);
  expect(onDidMount).toHaveBeenCalledTimes(1)
});


test('AuthImplicit will check the CSRF token', () => {
  const props = {location: {hash: "#access_token=1234567&scope=user_read&state=123456&token_type=bearer"}};
  const loginUser = jest.fn();
  const enableRepository = true;
  const state = '123456';
  process.env.REACT_APP_CSRF_TOKEN = state;

  const wrapper = shallow(<Router>
                            <AuthImplicit loginUser={loginUser} 
                                          enableRepository={enableRepository} 
                                          {...props} />
                          </Router>);
});

