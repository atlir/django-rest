
'use strict';

angular.
module('gmailApp').
factory('Threads', ['$http', '$q', 'Auth', 'localStorageService',
    function($http, $q, Auth, localStorageService) {

        var threads = [];
        var getThreads = function(nextPageToken) {
            var params = {};
            if(nextPageToken) {
                params.nextPageToken = nextPageToken;
            }
            var deferred = $q.defer();
            const access_token = localStorageService.get('access_token');
            const refresh_token = localStorageService.get('refresh_token');

            if (typeof(access_token) === 'undefined' || typeof(refresh_token) === 'undefined' || access_token === null) {
                deferred.reject({error: 'Something is wrong'});
                return deferred.promise;
            }

            Auth.isAuthenticated().then((user) => {
                $http({
                    method: 'GET',
                    url: '/emails/',
                    headers: {
                        'Authorization': 'Bearer ' + access_token
                    },
                    params: params
                }).then((data) => {
                    this.threads = data.data;
                    deferred.resolve(this.threads);
                }).catch(() => {
                    deferred.reject({error: 'Something is wrong'});
                })
            });

            return deferred.promise;
        };

        return {
            getThreads: getThreads
        }
    }
]);