$(document).ready(function() {
    $.ajax({
        url: "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=GME&apikey="
    }).then(function(data) {
        const price = parseFloat(data['Global Quote']['05. price']).toFixed(2);
        const change = data['Global Quote']['09. change'];

        if(price >= 1000) {
            gme_stat = "leaving the solar system! 🚀🚀🚀🚀🚀💫🛸"
        }
        else if(price >= 420.69) {
            gme_stat = "on Mars! 🚀🚀🚀🚀🔥"
        }
        else if(price >= 200) {
            gme_stat = "on the moon. 🚀🚀🚀🌔 "
        }
        else if(price >= 100) {
            gme_stat = "in outer orbit. 🌍🚀🚀🛰"
        }
        else if(price >= 50) {
            gme_stat = "starting the rocket-ship. 🚀"
        }
        else {
            gme_stat = "still on earth. 💎🙌"
        }

        $('.gme-status').append(gme_stat);
        $('.gme-price').append(price)

        if(change > 0) {
            change_icon = '💹';
        }
        else if(change == 0) {
            change_icon = '💤';
        }
        else if(change < 0) {
            change_icon = '🔻';
        }

        document.title = `${change_icon}[\$${price}] GameStop`;
    });
});
