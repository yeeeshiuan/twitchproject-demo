/**
 * 
 * @authors 
 * chandre (chandre21cn@gmail.com) 
 * hain (hailiang.hl.wang@gmail.com)
 * @date    2017-04-09 21:01:20
 */

const express = require('express');
const bodyParser = require('body-parser');
const favicon = require('serve-favicon')
const app = express();
const path = require('path')
const router = require("./router");

// Serve static assets from the /public folder
app.use(favicon(path.join(__dirname, 'public', 'favicon.ico')))
app.use('/public', express.static(path.join(__dirname, '/public')))

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use("/", router)

let config = require("./config")
// 启动HTTP服务
let server = app.listen({
	port: config.port || 3000,
	host: config.host || "0.0.0.0"
}, () => {
	console.log('HanLP Service listening at http://%s:%s', server.address().address, server.address().port);
});