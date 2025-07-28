import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import '../services/mma_reddit_service.dart';
import '../models/mma_post.dart';
import '../models/mma_reddit_post.dart';

class MMAFeedProvider with ChangeNotifier {
  final MMARedditService _redditService = MMARedditService();
  
  // Core state
  List<MMAPost> _posts = [];
  String _selectedCategory = 'All';
  String _selectedSource = 'All'; // Reddit, Community, Both
  String? _selectedFighter;
  String? _selectedWeightClass;
  String _selectedSubreddit = 'ufc';
  bool _isLoading = false;
  bool _isFetching = false; // Prevent multiple simultaneous fetches
  String? _errorMessage;

  // Getters
  List<MMAPost> get posts => _posts;
  String get selectedCategory => _selectedCategory;
  String get selectedSource => _selectedSource;
  String? get selectedFighter => _selectedFighter;
  String? get selectedWeightClass => _selectedWeightClass;
  String get selectedSubreddit => _selectedSubreddit;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  // Computed properties
  List<MMAPost> get redditPosts => _posts.where((post) => post.postType == 'reddit').toList();
  List<MMAPost> get communityPosts => _posts.where((post) => post.postType == 'community').toList();
  List<MMAPost> get trendingPosts => _posts.where((post) => 
    post is MMARedditPost && (post as MMARedditPost).isHighQuality
  ).toList();

  // Category management
  void setCategory(String category) {
    if (_selectedCategory != category) {
      _selectedCategory = category;
      // Don't call notifyListeners here - fetchPosts will call it
    }
  }

  void setSource(String source) {
    if (_selectedSource != source) {
      _selectedSource = source;
      // Don't call notifyListeners here - fetchPosts will call it
    }
  }

  void setFighter(String? fighterId) {
    if (_selectedFighter != fighterId) {
      _selectedFighter = fighterId;
      // Don't call notifyListeners here - fetchPosts will call it
    }
  }

  void setWeightClass(String? weightClass) {
    if (_selectedWeightClass != weightClass) {
      _selectedWeightClass = weightClass;
      // Don't call notifyListeners here - fetchPosts will call it
    }
  }

  void setSubreddit(String subreddit) {
    if (_selectedSubreddit != subreddit) {
      _selectedSubreddit = subreddit;
      // Don't call notifyListeners here - fetchPosts will call it
    }
  }

  // Main content aggregation method
  Future<void> fetchPosts(BuildContext context) async {
    if (_isFetching) return; // Prevent multiple simultaneous fetches
    
    _isFetching = true;
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      List<MMAPost> allPosts = [];
      
      // Fetch Reddit posts if selected
      if (_selectedSource == 'All' || _selectedSource == 'Reddit') {
        List<MMARedditPost> redditPosts = [];
        
        if (_selectedFighter != null) {
          // Fetch fighter-specific posts
          redditPosts = await _redditService.fetchFighterPosts(_selectedFighter!);
        } else if (_selectedWeightClass != null) {
          // Fetch weight class posts
          redditPosts = await _redditService.fetchWeightClassPosts(_selectedWeightClass!);
        } else if (_selectedCategory != 'All') {
          // Fetch category-specific posts
          final category = _getCategoryFromString(_selectedCategory);
          redditPosts = await _redditService.fetchCategoryPosts(category);
        } else {
          // Fetch general posts from selected subreddit
          redditPosts = await _redditService.fetchRedditPosts(
            subreddit: _selectedSubreddit,
            limit: 25,
          );
        }
        
        allPosts.addAll(redditPosts);
        
        if (kDebugMode) {
          print('MMAFeedProvider: Fetched ${redditPosts.length} Reddit posts');
        }
      }
      
      // TODO: Fetch community posts when community service is implemented
      if (_selectedSource == 'All' || _selectedSource == 'Community') {
        // List<MMACommunityPost> communityPosts = await _communityService.getCommunityPosts(
        //   category: _selectedCategory == 'All' ? null : _selectedCategory,
        //   fighterId: _selectedFighter,
        //   weightClass: _selectedWeightClass,
        // );
        // allPosts.addAll(communityPosts);
        
        if (kDebugMode) {
          print('MMAFeedProvider: Community posts not yet implemented');
        }
      }
      
      // Filter and sort posts
      allPosts = _filterAndSortPosts(allPosts);
      
      _posts = allPosts;
      
      if (kDebugMode) {
        print('MMAFeedProvider: Total posts: ${_posts.length}');
      }
      
    } catch (e) {
      _posts = [];
      _errorMessage = 'Failed to fetch posts: $e';
      if (kDebugMode) {
        print('MMAFeedProvider: Error fetching posts: $e');
      }
    }

    _isLoading = false;
    _isFetching = false;
    notifyListeners();
  }

  // Fetch trending posts across all subreddits
  Future<void> fetchTrendingPosts(BuildContext context) async {
    if (_isFetching) return;
    
    _isFetching = true;
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final trendingPosts = await _redditService.fetchTrendingPosts();
      _posts = trendingPosts;
      
      if (kDebugMode) {
        print('MMAFeedProvider: Fetched ${trendingPosts.length} trending posts');
      }
      
    } catch (e) {
      _posts = [];
      _errorMessage = 'Failed to fetch trending posts: $e';
      if (kDebugMode) {
        print('MMAFeedProvider: Error fetching trending posts: $e');
      }
    }

    _isLoading = false;
    _isFetching = false;
    notifyListeners();
  }

  // Filter and sort posts based on current filters
  List<MMAPost> _filterAndSortPosts(List<MMAPost> posts) {
    List<MMAPost> filteredPosts = List.from(posts);
    
    // Apply category filter
    if (_selectedCategory != 'All') {
      final category = _getCategoryFromString(_selectedCategory);
      filteredPosts = filteredPosts.where((post) {
        if (post is MMARedditPost) {
          return post.categorizePost() == category;
        }
        return post.category == category;
      }).toList();
    }
    
    // Apply fighter filter
    if (_selectedFighter != null) {
      filteredPosts = filteredPosts.where((post) {
        if (post is MMARedditPost) {
          return post.extractFighterMentions().any((name) => 
              name.toLowerCase().contains(_selectedFighter!.toLowerCase()));
        }
        return post.fighterId == _selectedFighter || 
               post.content.toLowerCase().contains(_selectedFighter!.toLowerCase());
      }).toList();
    }
    
    // Apply weight class filter
    if (_selectedWeightClass != null) {
      filteredPosts = filteredPosts.where((post) {
        return post.weightClass?.toLowerCase() == _selectedWeightClass!.toLowerCase() ||
               post.content.toLowerCase().contains(_selectedWeightClass!.toLowerCase());
      }).toList();
    }
    
    // Sort posts by relevance and date
    filteredPosts.sort((a, b) {
      // First sort by engagement (for Reddit posts)
      if (a is MMARedditPost && b is MMARedditPost) {
        final engagementComparison = b.engagementScore.compareTo(a.engagementScore);
        if (engagementComparison != 0) return engagementComparison;
      }
      
      // Then sort by date (newest first)
      return b.createdAt.compareTo(a.createdAt);
    });
    
    return filteredPosts;
  }

  // Helper method to convert string to PostCategory
  PostCategory _getCategoryFromString(String categoryString) {
    switch (categoryString.toLowerCase()) {
      case 'fight results':
        return PostCategory.fightResults;
      case 'fighter news':
        return PostCategory.fighterNews;
      case 'event discussion':
        return PostCategory.eventDiscussion;
      case 'training content':
        return PostCategory.trainingContent;
      case 'championship news':
        return PostCategory.championshipNews;
      case 'fight predictions':
        return PostCategory.fightPredictions;
      case 'behind the scenes':
        return PostCategory.behindTheScenes;
      case 'general discussion':
        return PostCategory.generalDiscussion;
      case 'memes':
        return PostCategory.memes;
      case 'questions':
        return PostCategory.questions;
      default:
        return PostCategory.generalDiscussion;
    }
  }

  // Get available categories for UI
  List<String> getAvailableCategories() {
    return [
      'All',
      'Fight Results',
      'Fighter News',
      'Event Discussion',
      'Training Content',
      'Championship News',
      'Fight Predictions',
      'Behind the Scenes',
      'General Discussion',
      'Questions',
    ];
  }

  // Get available sources for UI
  List<String> getAvailableSources() {
    return ['All', 'Reddit', 'Community'];
  }

  // Get available subreddits for UI
  List<String> getAvailableSubreddits() {
    return ['ufc', 'MMA', 'Boxing'];
  }

  // Get available weight classes for UI
  List<String> getAvailableWeightClasses() {
    return [
      'Flyweight',
      'Bantamweight',
      'Featherweight',
      'Lightweight',
      'Welterweight',
      'Middleweight',
      'Light Heavyweight',
      'Heavyweight',
      'Women\'s Strawweight',
      'Women\'s Flyweight',
      'Women\'s Bantamweight',
      'Women\'s Featherweight',
    ];
  }

  // Clear all filters
  void clearFilters() {
    _selectedCategory = 'All';
    _selectedSource = 'All';
    _selectedFighter = null;
    _selectedWeightClass = null;
    _selectedSubreddit = 'ufc';
    notifyListeners();
  }

  // Clear error message
  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }

  // Refresh posts
  Future<void> refresh(BuildContext context) async {
    await fetchPosts(context);
  }

  // Get posts by category
  List<MMAPost> getPostsByCategory(PostCategory category) {
    return _posts.where((post) {
      if (post is MMARedditPost) {
        return post.categorizePost() == category;
      }
      return post.category == category;
    }).toList();
  }

  // Get posts by fighter
  List<MMAPost> getPostsByFighter(String fighterName) {
    return _posts.where((post) {
      if (post is MMARedditPost) {
        return post.extractFighterMentions().any((name) => 
            name.toLowerCase().contains(fighterName.toLowerCase()));
      }
      return post.fighterId == fighterName || 
             post.content.toLowerCase().contains(fighterName.toLowerCase());
    }).toList();
  }

  // Get high-quality posts
  List<MMAPost> getHighQualityPosts() {
    return _posts.where((post) {
      if (post is MMARedditPost) {
        return post.isHighQuality;
      }
      return post.content.length > 100; // Simple quality check for community posts
    }).toList();
  }

  // Get recent posts (last 7 days)
  List<MMAPost> getRecentPosts() {
    final weekAgo = DateTime.now().subtract(const Duration(days: 7));
    return _posts.where((post) => post.createdAt.isAfter(weekAgo)).toList();
  }
} 