import React from 'react';
import { shallow, mount } from 'enzyme';

import TwitchEmbedVideo from '../TwitchEmbedVideo';


const twitchEmbedVideoProps={
        /** Optional for VOD embeds; otherwise, required. 
            Name of the chat room and channel to stream. */
        channel: "test",
        /** Width of video embed including chat */
        width: "940",
        /** Maximum width of the rendered element, in pixels. 
            This can be expressed as a percentage, by passing a string like 100% */
        height: "480",
        /** If true, the player can go full screen. Default: true. */
        allowfullscreen: false,
        /** Determines the screen layout. Valid values:
            video-and-chat: Default if channel is provided. Shows both video and chat side-by-side. 
              At narrow sizes, chat renders under the video player.
          * video: Default if channel is not provided. Shows only the video player (omits chat). */
        layout: "video-with-chat",
        /** The Twitch embed color theme to use. Valid values: light or dark. Default: light. */
        theme: "dark",
      };

test('TwitchEmbedVideo renders without crashing', () => {
  const wrapper = shallow(<TwitchEmbedVideo/>);
});

test('TwitchEmbedVideo will call componentDidMount when mounted', () => {
  const onDidMount = jest.fn();
  TwitchEmbedVideo.prototype.componentDidMount = onDidMount;
  const wrapper = mount(<TwitchEmbedVideo/>);
  expect(onDidMount).toHaveBeenCalledTimes(1)
});

test('TwitchEmbedVideo will call componentDidUpdate when props updated', () => {
  const onDidUpdate = jest.fn();
  TwitchEmbedVideo.prototype.componentDidUpdate = onDidUpdate;
  const wrapper = mount(<TwitchEmbedVideo {...twitchEmbedVideoProps}/>);
  wrapper.setProps({ twitchEmbedVideoProps: {channel: 'testme'} });
  expect(onDidUpdate).toHaveBeenCalledTimes(1)
});
