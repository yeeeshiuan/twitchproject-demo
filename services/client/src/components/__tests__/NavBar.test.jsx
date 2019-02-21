import React from 'react';
import { shallow } from 'enzyme';
import renderer from 'react-test-renderer';
import { MemoryRouter as Router } from 'react-router-dom';

import NavBar from '../NavBar';


test('NavBar renders properly', () => {
  const title = 'Hello, World!';
  const wrapper = shallow(<NavBar title={title}/>);
  const element = wrapper.find('Link');
  expect(element.length).toBe(2);
  expect(element.get(0).props.children).toBe(title);
  expect(element.get(1).props.children).toBe('About');
});

test('NavBar When not authenticated', () => {
  const isAuthenticated = false
  const title = 'Hello, World!';
  const twitchOAuthImplicit = 'http://tests.are.passing/callback'
  const wrapper = shallow(<NavBar title={title}
                                  isAuthenticated={isAuthenticated}
                                  twitchOAuthImplicit={twitchOAuthImplicit} />);

  const a = wrapper.find('a');
  expect(a.length).toBe(1);
  expect(a.get(0).props.children).toBe('Log In By Twitch');
  expect(a.get(0).props.href).toBe(twitchOAuthImplicit);

  const element = wrapper.find('Link');
  expect(element.length).toBe(2);
  expect(element.get(0).props.to).toBe('/');
  expect(element.get(0).props.children).toBe('Hello, World!');
  expect(element.get(1).props.to).toBe('#');
  expect(element.get(1).props.children).toBe('About');
});

test('NavBar When authenticated', () => {
  const isAuthenticated = true
  const title = 'Hello, World!';
  const wrapper = shallow(<NavBar isAuthenticated={isAuthenticated}
                                  title={title} />);
  const element = wrapper.find('Link');
  expect(element.length).toBe(3);
  expect(element.get(0).props.to).toBe('/');
  expect(element.get(0).props.children).toBe('Hello, World!');
  expect(element.get(1).props.to).toBe('#');
  expect(element.get(1).props.children).toBe('About');
  expect(element.get(2).props.to).toBe('/logout');
  expect(element.get(2).props.children).toBe('Log Out Here!');
});

test('NavBar renders a snapshot properly', () => {
  const tree = renderer.create(
    <Router location="/"><NavBar/></Router>
  ).toJSON();
  expect(tree).toMatchSnapshot();
});
