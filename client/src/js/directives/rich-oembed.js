/**
 * @ngdoc function
 * @name miller.directives:rich-oembed
 * @description
 * # richOembed
 * Rich oembed directive, with autoplay. Includes embedit directive as well.
 */
angular.module('miller')
  .directive('richOembed', function($sce, $log, $timeout, RUNTIME) {
    return {
      restrict : 'A',
      scope:{
        enabled: '=',
        oembed: '=',
        cover: '='
      },
      templateUrl: RUNTIME.static + 'templates/partials/directives/rich-oembed.html',
      
      link: function(scope, element, attrs) {
        // scope.enabled = false;
        var timer;

        scope.iframeEnabled = false;


        $log.log('🍩 rich-oembed ready', scope.cover);
        scope.$watch('enabled', function(v){
          $log.debug('🍩 rich-oembed @enabled:', v);
          scope.toggleEnable(!!v);
        });

        scope.toggleEnable = function(enabled){
          $log.log('🍩 rich-oembed > toggleEnable()', enabled);
          var v = enabled === undefined? !scope.iframeEnabled:  enabled;
          if(timer)
            $timeout.cancel(timer);
          timer = $timeout(function(){

            $log.log('🍩 rich-oembed apply iframeEnabled:', v);
            scope.iframeEnabled = v
          }, 500);
        }
      }
    }
  });
