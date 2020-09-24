var imgoffsetx=0;
var imgoffsety=0;
var signal_max=0;
var signal_min=99999;
var noise_max=0;
var noise_min=99999;
var margin_max=0;
var margin_min=99999;

function getIE()
{
	var rv = -1;
	if (navigator.appName == 'Microsoft Internet Explorer')
	{
		var ua = navigator.userAgent;
		var re  = new RegExp("MSIE ([0-9]{1,}[\.0-9]{0,})");
		if (re.exec(ua) != null)
			rv = parseFloat( RegExp.$1 );
	}
	return rv;
}

function lines()
{
	var img = document.getElementById("rssi");
	var pos = {x: img.offsetLeft, y: img.offsetTop};
	while((img = img.offsetParent)) {
		pos.x += img.offsetLeft;
		pos.y += img.offsetTop;
	}
	imgoffsetx = pos.x;
	imgoffsety = pos.y;

	var ver=getIE();
	if (ver != -1)
	{
		imgoffsetx += 6;
		imgoffsety += 6;
	}

	var linesstatechange = function(req) {
		var output=req.responseText;
		var arr=(output.split(/;/));
		if (arr[0]<1 || arr[0]>100) arr[0] = 1;
		if (arr[1]<1 || arr[1]>100) arr[1] = 1;
		if (arr[2]<1 || arr[2]>100) arr[2] = 1;

//		arr[0]=Math.floor(Math.random()*100 + 1);
//		arr[1]=Math.floor(Math.random()*100 + 1);
//		arr[2]=Math.floor(Math.random()*100 + 1);
		drawSignal(arr[0]/1);
		drawNoise(arr[1]/1);
		drawMargin(arr[2]/1);

		if(document.getElementById("start_stop_button").value == 'Stop') setTimeout("lines()", 1000);
	}

	runcmd("/cgi-bin/iwinfo.sh", linesstatechange);
}

function drawSignal(idx)
{
	var offsetx=imgoffsetx + 68;
	var offsety=imgoffsety + 72;

	if (idx > signal_max) signal_max=idx;
	drawLine('divsignalmax', offsetx, (offsety + signal_max), '#ffffff');

	if (idx < signal_min) signal_min=idx;
	drawLine('divsignalmin', offsetx, (offsety + signal_min), '#ffffff');

	drawLine('divsignalidx', offsetx, (offsety + idx), '#000');
}

function drawNoise(idx)
{
	var offsetx=imgoffsetx + 103;
	var offsety=imgoffsety + 72;

	if (idx > noise_max) noise_max=idx;
	drawLine('divnoisemax', offsetx, (offsety + noise_max), '#ffffff');

	if (idx < noise_min) noise_min=idx;
	drawLine('divnoisemin', offsetx, (offsety + noise_min), '#ffffff');

	drawLine('divnoiseidx', offsetx, (offsety + idx), '#000');
}

function drawMargin(idx)
{
	var offsetx=imgoffsetx + 151;
	var offsety=imgoffsety + 72;

	if (idx > margin_max) margin_max=idx;
	drawLine('divmarginmax', offsetx, (offsety + margin_max), '#ffffff');

	if (idx < margin_min) margin_min=idx;
	drawLine('divmarginmin', offsetx, (offsety + margin_min), '#ffffff');

	drawLine('divmarginidx', offsetx, (offsety + idx), '#000');
}

function drawLine(name, offsetx, offsety, color)
{
	var div = document.getElementById(name);
	if (div == null) 
	{
		var portion = "<div id="+name+" style='position:absolute;left:"+ offsetx +"px;top:"+ offsety +"px;width:21px;height:2px;background:"+color+"'><table height=1 width=1></table></div>";
		document.getElementById("divrssi").innerHTML += portion;
		div = document.getElementById(name);
	}

	if(document.getElementById("start_stop_button").value == 'Start')
	{
		document.getElementById("divrssi").removeChild(div);
	}
	else
	{
		div.style.left=offsetx;
		div.style.top=offsety;
		div.style.background=color;
//		div.style.display="none";
//		div.style.display="block";
	}
}

function proofreadText(input, proofFunction, validReturnCode)
{
	if(input.disabled != true)
	{
		input.style.color = (proofFunction(input.value) == validReturnCode) ? "black" : "red";
	}
}

function validateText(text)
{
	var errorCode = 0;
	if((text.length > 30) || (text.length < 1))
	{
		errorCode = 1;
	}
	for (i = 0; i < text.length; i++)
	{
		var c = text.charAt(i);
		if(c == ' ') errorCode=2;
	}
	return errorCode;
}

function validateNumber(number)
{
	var errorCode = 0;
	for (i = 0; i < number.length; i++)
	{
		var c = number.charAt(i);
		if((c < '0') || (c > '9')) errorCode=2;
	}
	if((number > 30) || (number < 1))
	{
		errorCode = 1;
	}
	return errorCode;
}

function proofreadInput(input)
{
	proofreadText(input, validateText, 0);
}

function proofreadNumber(input)
{
	proofreadText(input, validateNumber, 0);
}

function runcmd(cmd, statechange)
{
	var req;
	try {req = new XMLHttpRequest();} catch (e) {
		try {req = new ActiveXObject("Msxml2.XMLHTTP");} catch (e) {
			try {req = new ActiveXObject("Microsoft.XMLHTTP");} catch (e) {
				alert("Old browser...");
				return false;
			}
		}
	}

	req.onreadystatechange = function() {
		if (req.readyState == 4)
		{
			statechange(req);
		}
	}

	req.open("GET", cmd);
	req.setRequestHeader( "If-Modified-Since", "Sat, 1 Jan 2000 00:00:00 GMT" );
	req.send(null);
}

function showdata()
{

	var showdatastatechange = function(req)
	{
		var output=req.responseText;
		var arr=(output.split(/;/));
		
		document.getElementById("groupid").value = arr[0];
		if (arr[1] == 157)
		{
			document.getElementById("channel149").checked = false;
			document.getElementById("channel157").checked = true;
		} else {
			document.getElementById("channel149").checked = true;
			document.getElementById("channel157").checked = false;
		}
		document.getElementById("adjpower").value = arr[2];
	}

	runcmd("/cgi-bin/getvalues.sh", showdatastatechange);
}

function setChannel(radio)
{
	if (radio.value == 'channel149') {document.getElementById("channel157").checked = false;document.getElementById("channel149").checked = true;}
	if (radio.value == 'channel157') {document.getElementById("channel149").checked = false;document.getElementById("channel157").checked = true;}
}

function startGraph()
{
	var btn = document.getElementById("start_stop_button");
	if (btn.value == 'Start')
	{
		btn.value = 'Stop';
		lines();
	}
	else
	{
		btn.value = 'Start';
	}
}

function savedata()
{
	var groupid = document.getElementById("groupid");
	if (validateText(groupid.value) != 0)
	{
		alert("Wrong GroupID!");
		return;
	}
	var channel = document.getElementById("channel149").checked ? "149":"157";
	var power = document.getElementById("adjpower")
	if (validateNumber(power.value) != 0)
	{
		alert("Wrong Power Output!");
		return;
	}

	var pass1 = document.getElementById("password1").value;
	var pass2 = document.getElementById("password2").value;
	if (pass1 != "")
	{
		if (pass1 != pass2)
		{
			alert("Password not match. Try again.");
			return;
		}
	}
	else
	{
		pass1 = '--empty--';
	}

	var cmd = groupid.value+';'+channel+';'+power.value+';'+pass1;

	var savedatastatechange = function(req)
	{
		document.getElementById("password1").value = "";
		document.getElementById("password2").value = "";
	}

	runcmd("/cgi-bin/setvalues.sh?" + fullEscape(cmd+"\n"), savedatastatechange);
}

function fullEscape(str)
{
	str = encodeURIComponent(str);
	var otherEscape = [ '*', '@', '-', '_', '+', '.', '/' ];
	var otherEscaped= [ '2A','40','2D','5F','2B','2E','2F'];
	for(oeIndex=0; oeIndex < otherEscape.length; oeIndex++)
	{
		var splitStr = str.split( otherEscape[oeIndex] );
		if(splitStr.length > 1)
		{
			str = splitStr.join( "%" + otherEscaped[oeIndex] );
		}
	}
	return str;
}

function login()
{
	var user = document.getElementById("username").value;
	var pass = document.getElementById("password").value;

	if (user != "admin")
	{
		alert ("Wrong User Name or Password!");
		return;
	}

	var loginstatechange = function(req)
	{
		var output=req.responseText;
		if (output.indexOf("OK") != -1)
		{
			document.getElementById("login").style.display="none";
			document.getElementById("configuration").style.display="block";
			document.getElementById("signal").style.display="block";
		}
		else
		{
			alert ("Wrong User Name or Password!");
			return;
		}
	}

	runcmd("/cgi-bin/login.sh?" + fullEscape(pass+"\n"), loginstatechange);
}
