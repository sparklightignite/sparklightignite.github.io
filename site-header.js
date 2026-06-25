(function () {
  var target = document.getElementById('site-header');
  if (!target) return;
  var scripts = document.getElementsByTagName('script');
  var script = scripts[scripts.length - 1];
  var base = script && script.src ? script.src.replace(/[^/]*$/, '') : './';
  target.innerHTML = '<header class="site-header"><div class="wrap"><img class="banner" src="' + base + 'banner-logo.png" alt="Spark Light Ignite Studios" /><nav aria-label="Main navigation"><a href="https://www.facebook.com/SparkLightIgniteStudios" target="_blank" rel="noopener noreferrer">Facebook</a><a href="https://www.tiktok.com/@spark.light.ignite" target="_blank" rel="noopener noreferrer">TikTok</a><a href="https://x.com/SLI_STUDIOS" target="_blank" rel="noopener noreferrer">X.COM</a><a href="https://www.youtube.com/@SparkLightIgniteStudios" target="_blank" rel="noopener noreferrer">YouTube</a><a href="' + base + '">Home</a><a href="' + base + 'contact.html">Contact</a></nav></div></header>';
}());
