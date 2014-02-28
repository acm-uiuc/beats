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

function BeatsController($scope, $http)
{
    $scope.sections =
    [
        { title: 'Queue', icon: '\uf03a' },
        { title: 'Recently Added', icon: '\uf017' },
        { title: 'Recently Played', icon: '\uf04b' },
        { title: 'Random', icon: '\uf074' },
        { title: 'Top 100', icon: '\uf01b' },
    ];

    var songs =
    [
        makeSong('Waltz of the Flowers', 'The Nutcraker', 8, 'Tchaikovsky', 410),
        makeSong('March of the Mephisto', 'The Black Halo', 1, 'Kamelot', 329),
    ];

    for (var i = 0; i < 100; i++)
    {
        songs[i + 2] = JSON.parse(JSON.stringify(songs[0]));
        songs[i + 2].trackNum = Math.floor(Math.random() * 20) + 1;
        songs[i + 2].vote = (Math.random() < 0.5);
    }

    $scope.playlists =
    [
        { title: 'Rock' },
        { title: 'Pop' },
        { title: 'Top 40' },
        { title: 'Hardcore' },
        { title: 'Witch-Hop' },
    ];

    $scope.playlist = songs;

    $scope.volumePercentage = 0.5;
    $scope.playbackTime = 50;
    $scope.playbackDuration = 100;
};
