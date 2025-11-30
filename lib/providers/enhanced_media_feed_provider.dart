import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import '../services/enhanced_media_service.dart';
import '../services/mma_reddit_service.dart';
import '../models/media_post.dart';
import '../models/media_feed_result.dart';
import '../models/mma_post.dart';
import '../models/mma_reddit_post.dart';

class EnhancedMediaFeedProvider with ChangeNotifier {
  final EnhancedMediaService _mediaService = EnhancedMediaService();
  final MMARedditService _redditService = MMARedditService();
  
  // Core state
  List<dynamic> _allPosts = []; // Mix of MediaPost and MMARedditPost
  String _selectedPlatform = 'All'; // All, YouTube, Twitter, TikTok, Reddit
  String _selectedCategory = 'All';
  String? _selectedEvent;
  List<String>? _selectedFighters;
  bool _isLoading = false;
  bool _isFetching = false;
  String? _errorMessage;
  
  // Getters
  List<dynamic> get allPosts => _allPosts;
  String get selectedPlatform => _selectedPlatform;
  String get selectedCategory => _selectedCategory;
  String? get selectedEvent => _selectedEvent;
  List<String>? get selectedFighters => _selectedFighters;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  
  // Computed properties
  List<MediaPost> get mediaPosts => _allPosts.whereType<MediaPost>().toList();
  List<MMARedditPost> get redditPosts => _allPosts.whereType<MMARedditPost>().toList();
  
  List<dynamic> get filteredPosts {
    List<dynamic> posts = List.from(_allPosts);
    
    // Filter by platform
    if (_selectedPlatform != 'All') {
      posts = posts.where((post) {
        if (post is MediaPost) {
          return post.platform.toLowerCase() == _selectedPlatform.toLowerCase();
        } else if (post is MMARedditPost) {
          return _selectedPlatform.toLowerCase() == 'reddit';
        }
        return false;
      }).toList();
    }
    
    // Filter by category
    if (_selectedCategory != 'All') {
      posts = posts.where((post) {
        if (post is MediaPost) {
          return post.contentType.toLowerCase() == _selectedCategory.toLowerCase();
        } else if (post is MMARedditPost) {
          return post.categorizePost().toString().split('.').last.toLowerCase() == _selectedCategory.toLowerCase();
        }
        return false;
      }).toList();
    }
    
    return posts;
  }
  
  // Platform management
  void setPlatform(String platform) {
    if (_selectedPlatform != platform) {
      _selectedPlatform = platform;
      notifyListeners();
    }
  }
  
  void setCategory(String category) {
    if (_selectedCategory != category) {
      _selectedCategory = category;
      notifyListeners();
    }
  }
  
  void setEvent(String? event) {
    if (_selectedEvent != event) {
      _selectedEvent = event;
      notifyListeners();
    }
  }
  
  void setFighters(List<String>? fighters) {
    if (_selectedFighters != fighters) {
      _selectedFighters = fighters;
      notifyListeners();
    }
  }
  
  // Main content aggregation method
  Future<void> fetchAllContent(BuildContext context) async {
    if (_isFetching) return;
    
    _isFetching = true;
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();
    
    try {
      List<dynamic> allContent = [];
      
      // Fetch from enhanced media scraper (YouTube, Twitter, TikTok)
      if (_selectedPlatform == 'All' || 
          ['YouTube', 'Twitter', 'TikTok'].contains(_selectedPlatform)) {
        try {
          final mediaResult = await _mediaService.fetchComprehensiveContent(
            eventName: _selectedEvent,
            fighterNames: _selectedFighters,
            maxPerPlatform: 20,
          );
          
          if (!mediaResult.hasError) {
            allContent.addAll(mediaResult.content);
            if (kDebugMode) {
              print('EnhancedMediaFeedProvider: Fetched ${mediaResult.content.length} media posts');
            }
          } else {
            print('Media scraping error: ${mediaResult.error}');
          }
        } catch (e) {
          print('Error fetching media content: $e');
        }
      }
      
      // Fetch Reddit posts if selected
      if (_selectedPlatform == 'All' || _selectedPlatform == 'Reddit') {
        try {
          List<MMARedditPost> redditPosts = [];
          
          if (_selectedFighters != null && _selectedFighters!.isNotEmpty) {
            // Fetch fighter-specific posts
            for (final fighter in _selectedFighters!.take(2)) {
              final posts = await _redditService.fetchFighterPosts(fighter);
              redditPosts.addAll(posts);
            }
          } else if (_selectedEvent != null) {
            // Fetch event-specific posts
            redditPosts = await _redditService.fetchRedditPosts(
              subreddit: 'ufc',
              limit: 25,
            );
          } else {
            // Fetch general posts
            redditPosts = await _redditService.fetchRedditPosts(
              subreddit: 'ufc',
              limit: 25,
            );
          }
          
          allContent.addAll(redditPosts);
          
          if (kDebugMode) {
            print('EnhancedMediaFeedProvider: Fetched ${redditPosts.length} Reddit posts');
          }
        } catch (e) {
          print('Error fetching Reddit content: $e');
        }
      }
      
      // Sort by relevance and recency
      allContent.sort((a, b) => _calculateRelevanceScore(b).compareTo(_calculateRelevanceScore(a)));
      
      _allPosts = allContent;
      
      if (kDebugMode) {
        print('EnhancedMediaFeedProvider: Total content loaded: ${_allPosts.length}');
      }
      
    } catch (e) {
      _errorMessage = 'Failed to load content: $e';
      if (kDebugMode) {
        print('EnhancedMediaFeedProvider error: $e');
      }
    } finally {
      _isLoading = false;
      _isFetching = false;
      notifyListeners();
    }
  }
  
  double _calculateRelevanceScore(dynamic post) {
    double score = 0.0;
    DateTime now = DateTime.now();
    
    if (post is MediaPost) {
      // Enhanced media post scoring
      score += post.relevanceScore * 0.4;
      score += post.sourcePriority * 10;
      
      // Recency bonus
      final hoursSince = now.difference(post.publishedAt).inHours;
      if (hoursSince < 24) score += 30;
      else if (hoursSince < 72) score += 15;
      
      // Engagement bonus
      score += (post.viewCount / 1000) * 0.2;
      score += (post.likeCount / 100) * 0.3;
      
    } else if (post is MMARedditPost) {
      // Reddit post scoring
      score += post.engagementScore * 0.3;
      score += (post.redditScore * 0.2);
      score += (post.redditComments * 0.1);
      
      if (post.isRecent) score += 20;
      if (post.isHighQuality) score += 15;
    }
    
    return score;
  }
  
  // Clear all filters
  void clearFilters() {
    _selectedPlatform = 'All';
    _selectedCategory = 'All';
    _selectedEvent = null;
    _selectedFighters = null;
    notifyListeners();
  }
  
  // Clear error message
  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }
  
  // Refresh posts
  Future<void> refresh(BuildContext context) async {
    await fetchAllContent(context);
  }
  
  // Get available platforms for UI
  List<String> getAvailablePlatforms() {
    return ['All', 'YouTube', 'Twitter', 'TikTok', 'Reddit'];
  }
  
  // Get available categories for UI
  List<String> getAvailableCategories() {
    return [
      'All',
      'Highlights',
      'Interview',
      'News',
      'Analysis',
      'Event',
      'Podcast',
      'General',
    ];
  }
  
  // Get posts by platform
  List<dynamic> getPostsByPlatform(String platform) {
    return _allPosts.where((post) {
      if (post is MediaPost) {
        return post.platform.toLowerCase() == platform.toLowerCase();
      } else if (post is MMARedditPost) {
        return platform.toLowerCase() == 'reddit';
      }
      return false;
    }).toList();
  }
  
  // Get posts by category
  List<dynamic> getPostsByCategory(String category) {
    return _allPosts.where((post) {
      if (post is MediaPost) {
        return post.contentType.toLowerCase() == category.toLowerCase();
      } else if (post is MMARedditPost) {
        return post.categorizePost().toString().split('.').last.toLowerCase() == category.toLowerCase();
      }
      return false;
    }).toList();
  }
  
  // Get high-priority content
  List<dynamic> getHighPriorityContent() {
    return _allPosts.where((post) {
      if (post is MediaPost) {
        return post.sourcePriority >= 4;
      } else if (post is MMARedditPost) {
        return post.isHighQuality;
      }
      return false;
    }).toList();
  }
  
  // Get recent content
  List<dynamic> getRecentContent({int hours = 24}) {
    final cutoff = DateTime.now().subtract(Duration(hours: hours));
    return _allPosts.where((post) {
      if (post is MediaPost) {
        return post.publishedAt.isAfter(cutoff);
      } else if (post is MMARedditPost) {
        return post.redditCreated.isAfter(cutoff);
      }
      return false;
    }).toList();
  }
  
  // Get content statistics
  Map<String, int> getContentStats() {
    final stats = <String, int>{};
    
    for (final post in _allPosts) {
      if (post is MediaPost) {
        stats[post.platform] = (stats[post.platform] ?? 0) + 1;
        stats[post.contentType] = (stats[post.contentType] ?? 0) + 1;
      } else if (post is MMARedditPost) {
        stats['reddit'] = (stats['reddit'] ?? 0) + 1;
      }
    }
    
    return stats;
  }
}
