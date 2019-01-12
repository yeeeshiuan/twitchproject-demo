import React, { Component } from 'react';
const EMBED_URL = 'https://embed.twitch.tv/embed/v1.js';

class TwitchEmbedVideo extends Component {
    constructor() {
        super();
        this.state = {
            channel:"",
        }
    };

    static defaultProps = {
        targetClass: 'twitch-embed'
    };

    componentDidMount() {
        
        this.setState({channel: this.props.channel});

        let embed;
        if (window.Twitch && window.Twitch.Embed) {
            console.log("componentDidMount_if");
            embed = new window.Twitch.Embed(this.props.targetClass, { ...this.props });
            this._addEventListeners(embed);
        } else {
            console.log("componentDidMount_else");
            const script = document.createElement('script');
            script.setAttribute(
                'src',
                EMBED_URL
            );
            script.addEventListener('load', () => {
                embed = new window.Twitch.Embed(this.props.targetClass, { ...this.props });
                this._addEventListeners(embed);
            });

            document.body.appendChild(script);
        }
    }

    componentDidUpdate() {
        let embed;
        if (this.state.channel !== this.props.channel) {
            /** update temp channel **/
            this.setState({channel: this.props.channel});
            /** remove old stream **/
            const mainDiv = document.getElementById(this.props.targetClass);
            mainDiv.removeChild(mainDiv.childNodes[0]);
            /** create new stream **/
            const script = document.createElement('script');
            script.setAttribute(
                'src',
                EMBED_URL
            );
            script.addEventListener('load', () => {
                embed = new window.Twitch.Embed(this.props.targetClass, { ...this.props });
                this._addEventListeners(embed);
            });

            document.body.appendChild(script);
        }
    }

    _addEventListeners(embed) {
        embed.addEventListener(window.Twitch.Embed.AUTHENTICATE, function(user) {
            if (this.props.onUserLogin) {
                this.props.onUserLogin(user);
            }
        }.bind(this));        

        embed.addEventListener(window.Twitch.Embed.VIDEO_PLAY, function(data) {
            if (this.props.onVideoPlay) {
                this.props.onVideoPlay(data);
            }
        }.bind(this));

        /** Player ready for programmatic commands */     
        embed.addEventListener(window.Twitch.Embed.VIDEO_READY, function() {
            var player = embed.getPlayer();

            if (this.props.onPlayerReady) {
                this.props.onPlayerReady(player);
            }
        }.bind(this));        
    }

    render() {
        return (
            <div id={this.props.targetClass}></div>
        );
    }
}

export default TwitchEmbedVideo;
