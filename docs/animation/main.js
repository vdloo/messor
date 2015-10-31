var max_ticks = 500;

function render_image(ctx, asset) {
	if (asset.img.complete == true) {
		alpha = ctx.globalAlpha;
		ctx.globalAlpha = asset.loc.a;
		ctx.drawImage(asset.img, asset.loc.x, asset.loc.y);
		ctx.globalAlpha = alpha;
	}
};

function load_asset(asset_src) {
	var asset = new Image();
	asset.src = asset_src;
	return {loc: {x: 0, y: 0, a: 1.0}, img: asset};
}

function load_file() {
	return load_asset('assets/file.png');
}

function load_phone() {
	return load_asset('assets/phone.png');
}

function load_desktop() {
	return load_asset('assets/desktop.png');
}

function load_assets() {
	var car = load_phone();
	var dst = load_desktop();
	var src = load_desktop();
	var ff1 = load_file();
	var ft1 = load_file();

	fis = {ff1: ff1, ft1: ft1};
	assets = {car: car, src: src, dst: dst, fis: fis};
	return assets;
}

function clear(ctx) {
	ctx.clearRect(0, 0, c1.width, c1.height);
	ctx.fillStyle = "rgb(255, 255, 255)";
	ctx.fillRect(0, 0, c1.width, c1.height);
}

function reset(assets) {
	assets.src.loc.x = 0;
	assets.src.loc.y = 60;

	assets.dst.loc.x = 435;
	assets.dst.loc.y = 60;

	assets.car.loc.x = 56;
	assets.car.loc.y = 60;

	assets.fis.ff1.loc.x = 0;
	assets.fis.ff1.loc.y = -3;

	assets.fis.ft1.loc.x = max_ticks - 65;
	assets.fis.ft1.loc.y = 125;
}

function draw (ticks, direction, ctx, assets) {
	if (ticks == -400) {
		reset(assets);
	}
	if (ticks < -250 && ticks > -350) {
		if (direction) {
			assets.fis.ff1.loc.a += 0.01;
			assets.fis.ft1.loc.a += 0.01;
		} else {
			assets.fis.ff1.loc.a -= 0.01;
			assets.fis.ft1.loc.a -= 0.01;
		}
	}
	if (ticks > 55 && ticks < max_ticks - 125) {
		assets.car.loc.x = ticks;
	}
	if (ticks > 0 && ticks < max_ticks - 65) {
		if (direction) {
			assets.fis.ff1.loc.x = ticks;
		} else {
			assets.fis.ft1.loc.x = ticks;
		}
	}
	render_image(ctx, assets.fis.ff1);

	render_image(ctx, assets.fis.ft1);

	render_image(ctx, assets.car);
	render_image(ctx, assets.src);
	render_image(ctx, assets.dst);
};

function manage_direction (direction, ticks) {
	if (ticks < -500 || ticks > max_ticks) {
		direction = !direction;
	}
	return direction;
}

function animate (ticks, direction, ctx, assets, encoder) {
	clear(ctx);
	draw(ticks, direction, ctx, assets);
	if (ticks % 2 == 0) {
		encoder.addFrame(ctx);
		console.log('adding frame');
	}
	direction = manage_direction(direction, ticks);
	direction ? ticks ++ : ticks--;
	if (direction && ticks == -201) {
		encoder.finish();
		var binary_gif = encoder.stream().getData();
		var data_url = 'data:image/gif;base64,'+encode64(binary_gif);
		document.body.innerHTML = "<img src='" + data_url + "' alt='Animation'/>";
	} else {
		setTimeout(function() {
			animate(ticks, direction, ctx, assets, encoder);
		}, 5);
	}
}

window.onload = function() {
	var encoder = new GIFEncoder();
	encoder.setRepeat(0);
	encoder.setDelay(16.66);
	encoder.start();


	var c1 = document.getElementById('c1');
	var ctx = c1.getContext('2d');

	assets = load_assets();

	reset(assets);
	animate(-200, true, ctx, assets, encoder);
}
