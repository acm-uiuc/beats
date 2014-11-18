var snowFlakes = [];

var lastTime = null;

document.addEventListener("DOMContentLoaded", function(event)
{
    for (var i = 0; i < 100; i++)
    {
        var snowFlakeElement = document.createElement("div");
        snowFlakeElement.style.position = "absolute";
        snowFlakeElement.style.backgroundColor = "white";
        snowFlakeElement.style.zIndex = 100;
        document.body.appendChild(snowFlakeElement);

        snowFlakes.push(spawnSnowFlake({ element: snowFlakeElement }));
    }

    window.requestAnimationFrame(animateSnow);
});

function randRange(min, max)
{
    return Math.random() * (max - min) + min;
}

function spawnSnowFlake(snowFlake)
{
    snowFlake.x = randRange(0, document.body.clientWidth);
    snowFlake.y = randRange(-document.body.clientHeight, 0);
    snowFlake.size = randRange(1, 10);
    snowFlake.speed = randRange(10, 100);
    return snowFlake;
}

function animateSnowFlake(dt, snowFlake)
{
    snowFlake.y += dt * snowFlake.speed;
    snowFlake.x += Math.sin(snowFlake.y / 100) * dt * (100 - snowFlake.speed);
    if (snowFlake.x + snowFlake.size < 0)
    {
        snowFlake.x += document.body.clientWidth + snowFlake.size;
    }
    else if (snowFlake.x > document.body.clientWidth)
    {
        snowFlake.x -= document.body.clientWidth + snowFlake.size;
    }
    if (snowFlake.y > document.body.clientHeight)
    {
        spawnSnowFlake(snowFlake);
    }
    return snowFlake;
}

function applySnowFlake(snowFlake)
{
    snowFlake.element.style.width = snowFlake.size + "px";
    snowFlake.element.style.height = snowFlake.size + "px";
    snowFlake.element.style.left = snowFlake.x + "px";
    snowFlake.element.style.top = snowFlake.y + "px";
    snowFlake.element.style.borderRadius = (snowFlake.size / 2) + "px";
    return snowFlake;
}

function animateSnow(timestamp)
{
    if (!lastTime)
    {
        lastTime = timestamp;
        window.requestAnimationFrame(animateSnow);
        return;
    }

    var dt = (timestamp - lastTime) / 1000;
    lastTime = timestamp;

    for (var snowFlakeIndex = 0; snowFlakeIndex < snowFlakes.length; snowFlakeIndex++)
    {
        var snowFlake = snowFlakes[snowFlakeIndex];
        animateSnowFlake(dt, snowFlake);
        applySnowFlake(snowFlake);
    }

    window.requestAnimationFrame(animateSnow);
}

