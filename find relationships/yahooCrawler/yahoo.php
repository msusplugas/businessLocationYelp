<?php
/*
 * Import the array of categories for a state and then we make a yahoo request for each category
 *  we store the 50 results per request in a csv file.
 */
$csvFileNameInput = 'categoriesAZ.csv';

$arrayCategories = [];

$file = fopen($csvFileNameInput, 'r')  or die("Unable to open file!");
while (($line = fgetcsv($file, 0, ",", "'", '\\')) !== FALSE) {
    //$line is an array of the csv elements
    $arrayCategories = array_merge($arrayCategories, $line);
}
fclose($file);


/* Pre-requisite: Download the required PHP OAuth class from http://oauth.googlecode.com/svn/code/php/OAuth.php. This is used below */

require("OAuth.php");


$csvFileNameOutput = 'categoriesAZWithUrl.csv';
$myFile = fopen($csvFileNameOutput, "w") or die("Unable to open file!");
$counter = 0;

$trans = array("'" => "\'"); // We escape every quote

$header = "'category','link1','link2','link3','link4','link5','link6','link7','link8','link9','link10','link11','link12','link13','link14','link15','link16','link17','link18','link19','link20','link21','link22','link23','link24','link25','link26','link27','link28','link29','link30','link31','link32','link33','link34','link35','link36','link37','link38','link39','link40','link41','link42','link43','link44','link45','link46','link47','link48','link49','link50' \n";
fwrite($myFile,$header);

foreach ($arrayCategories as $category) {

    $category = str_replace("\\", "", $category); // We remove the backslash

    $cc_key  = "yourKey";
    $cc_secret = "yourSecret";
    $url = "https://yboss.yahooapis.com/ysearch/news,web,images";
    $args = [];
    $args["format"] = "json";
    $args["q"] = $category . " in Phoenix";
    $counter += 1;
    print_r($counter . ": " . $args["q"] ."\n");

    $consumer    = new OAuthConsumer($cc_key, $cc_secret);
    $request = OAuthRequest::from_consumer_and_token($consumer, NULL,"GET", $url, $args);
    $request->sign_request(new OAuthSignatureMethod_HMAC_SHA1(), $consumer, NULL);
    $url = sprintf("%s?%s", $url, OAuthUtil::build_http_query($args));
    $ch = curl_init();
    $headers = array($request->to_header());
    curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, TRUE);
    $rsp = curl_exec($ch);
    $results = json_decode($rsp, true);


    $category = strtr($category, $trans);
    $data = "'" . $category . "'";

    foreach ($results['bossresponse']['web']['results'] as $value) {
        $link =$value['url'];
        $link = strtr($link, $trans);
        $data .= ",'". $link . "'";
    }

    $data .= "\n";

    fwrite($myFile, $data);

    sleep(0.1);
}

fclose($myFile);

//print_r($results);

/*
$myFile = fopen("yahoo.txt", "w") or die("Unable to open file!");
$firstColumn = "'" . $query . "'" . ',';
fwrite($myFile, $firstColumn);

foreach ($results['bossresponse']['web']['results'] as $key=>$value) {
    $data = "'".$value['url'] ."'" . ',';
    fwrite($myFile, $data);
}



fclose($myFile);
*/
?>