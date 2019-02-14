import React from 'react';
import { shallow } from 'enzyme';
import { MemoryRouter as Router } from 'react-router-dom';
import renderer from 'react-test-renderer';
import { BarChart } from "react-d3-components";
jest.mock('react-d3-components');

import BarChartComponent from '../BarChartComponent';


test('BarChartComponent renders a snapshot properly', () => {
  const tree = renderer.create(<BarChartComponent/>).toJSON();
  expect(tree).toMatchSnapshot();
});

test('BarChartComponent renders without crashing', () => {
  const wrapper = shallow(<BarChartComponent/>);
});

test('BarChartComponent renders properly', () => {
  const wrapper = shallow(<BarChartComponent/>);
  const barChart = wrapper.find('BarChart');
  expect(barChart.length).toBe(1);
});
