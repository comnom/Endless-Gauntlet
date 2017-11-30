// Whether the changelog is shown
var state = 0;


// Github api get request for the latest release
function apiGetLatest() {
	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			var data = JSON.parse(this.responseText);
			document.getElementById("endless-gauntlet-zip").href = data.assets[0].browser_download_url;
			document.getElementById("endless-gauntlet-tar").href = 
			"https://github.com/comnom/Endless-Gauntlet/archive/" + data.tag_name + ".tar.gz";
			document.getElementById("current-version").innerHTML = 
			data.tag_name + " Released: " + data.published_at.split("T")[0];
			document.getElementById("changelog").innerHTML = data.body;
		}
	};
	xhttp.open("GET", "https://api.github.com/repos/comnom/Endless-Gauntlet/releases/latest", true);
	xhttp.setRequestHeader("Accept", "application/vnd.github.v3+json");
	xhttp.send();
}

// Toggle the changelog view
function toggleChangelog() {
	var img = document.getElementById("changelog-arrow");
	var pre = document.getElementById("changelog");
	if (state) {
		state = 0;
		img.style.transform = "none";
		pre.style.display = "none";
	}
	else {
		state = 1;
		img.style.transform = "rotate(180deg)";
		pre.style.display = "block";
	}
}
