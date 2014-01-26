<html>
<head>
	<script type="text/javascript" src="js/raphael-min.js"></script>
	<script type="text/javascript" src="js/dracula_graffle.js"></script>
	<script type="text/javascript" src="js/jquery-1.4.2.min.js"></script>
	<script type="text/javascript" src="js/dracula_graph.js"></script>

	<script type="text/javascript">
window.onload = function() {
	// var width = $(document).width() - 20;
	// var height = $(document).height() - 60;
	var width = 20000;
	var height = 16000;

	g = new Graph();

<?php

$db = new SQLite3("artists.db");
if ($db == null) {
	die("Unable to open the SQLite database file artists.db");
}

$result = $db->query("SELECT artist, similarity, match FROM similarities WHERE match > 0.5");
while (($row = $result->fetchArray())) {
	$artist = utf8_encode(str_replace('"', '\"', $row['artist']));
	$similarity = utf8_encode(str_replace('"', '\"', $row['similarity']));
	$match = $row['match'];
	print "\t" . 'g.addEdge("' . $artist . '", "' . $similarity . '", { directed: true, label: "' . $match . '" });' . "\n";
}

$db->close();

?>

	var layouter = new Graph.Layout.Spring(g);
	layouter.layout();
	 
	var renderer = new Graph.Renderer.Raphael('canvas', g, width, height);
	renderer.draw();
}
	</script>

</head>

<body>
<div id="canvas"></div>

</body>
</html>

