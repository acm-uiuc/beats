angular.module('Beats.filters', [])
// A filter that takes a number of seconds and converts it to MM:SS format
.filter('momentFormat', function()
{
    return function(input)
    {
        var seconds = (Math.floor(input) % 60);
        if (seconds < 10)
        {
            seconds = "0" + seconds;
        }
        return Math.floor(input / 60) + ":" + seconds;
    };
});

angular.module('BeatsApp', ['Beats.filters'])
.controller('BeatsController', ['$scope', '$http', '$interval', function($scope, $http, $interval)
{
    $scope.showDialog = false;
    $scope.loggedIn = false;
    $scope.playlist = [];
    $scope.queue = [];
    $scope.volumePercentage = 0.5;
    $scope.playbackTime = 0;
    $scope.playbackDuration = 100;

    $scope.sections =
    [
        { title: 'Queue', icon: '\uf03a' },
        { title: 'Recently Added', icon: '\uf017' },
        { title: 'Recently Played', icon: '\uf04b' },
        { title: 'Random', icon: '\uf074' },
        { title: 'Top 100', icon: '\uf01b' },
    ];

    $scope.playlists =
    [
        { title: 'Rock' },
        { title: 'Pop' },
        { title: 'Top 40' },
        { title: 'Hardcore' },
        { title: 'Witch-Hop' },
    ];

    $scope.searchSongs = function(query)
    {
        $http.get('/v1/songs/search',
        {
            params: { 'q': query }
        })
        .success(function(data)
        {
            var songs = [];
            for (var resultIndex = 0; resultIndex < data.results.length; resultIndex++)
            {
                var result = data.results[resultIndex];
                songs[resultIndex] = result;
            }
            $scope.playlist = songs;
        });
    }

    $scope.voteSong = function(song)
    {
        console.log(song);
        $http.post('/v1/queue/add', 'id=' + song._id,
        {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        })
        .success(function(data)
        {
            console.log(data);
        });
    };

    $scope.pauseSong = function()
    {
        $http.post('/v1/player/pause');
    };

    $scope.skipSong = function()
    {
        $http.post('/v1/player/play_next');
    };

    $interval(function()
    {
        $http.get('/v1/player/status')
        .success(function(data)
        {
            $scope.playbackTime = data['current_time'] / 1000;
            $scope.playbackDuration = data['duration'] / 1000;
        });

        $http.get('/v1/queue')
        .success(function(data)
        {
            $scope.queue = data['queue'].slice(data['position']);
        });
    }, 1000);
}]);

function makeSong(title, albumTitle, trackNum, artist, length)
{
    return {
        title:      title,
        albumTitle: albumTitle,
        trackNum:   trackNum,
        artist:     artist,
        length:     length,
    };
}

