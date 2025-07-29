import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../models/mma_reddit_post.dart';
import '../models/mma_post.dart';

class MMARedditService {
  // MMA-specific subreddit mapping
  static const Map<String, String> mmaSubredditMapping = {
    'Main Events': 'ufc',
    'Fight Analysis': 'MMA',
    'Fighter News': 'ufc',
    'Event Discussion': 'MMA',
    'Training': 'MMA',
    'Weight Classes': 'ufc',
    'Championship': 'ufc',
    'Prelims': 'ufc',
    'Fight Predictions': 'ufc',
    'Post-Fight': 'MMA',
    'Fighter Interviews': 'ufc',
    'Behind the Scenes': 'MMA',
  };

  // Primary MMA subreddits
  static const List<String> primarySubreddits = ['ufc', 'MMA', 'Boxing'];
  
  // Secondary MMA subreddits for broader content
  static const List<String> secondarySubreddits = ['ufcstats', 'MMAStreams', 'ufcbetting'];

  /// Fetch Reddit posts from MMA subreddits
  Future<List<MMARedditPost>> fetchRedditPosts({
    String subreddit = 'ufc',
    int limit = 20,
    String? category,
    String? fighterName,
    String? weightClass,
  }) async {
    try {
      // Use proper User-Agent and add delay to respect rate limits
      await Future.delayed(const Duration(milliseconds: 500));
      
      final url = Uri.https('www.reddit.com', '/r/$subreddit/hot.json', {
        'limit': '$limit',
        'raw_json': '1',
      });
      
      final response = await http.get(
        url, 
        headers: {
          'User-Agent': 'MMAApp/1.0 (by /u/mma_app_dev)',
          'Accept': 'application/json',
        },
      );
      
      if (response.statusCode != 200) {
        if (kDebugMode) {
          print('Reddit API error: ${response.statusCode} - ${response.body}');
        }
        throw Exception('Reddit API returned status ${response.statusCode}');
      }
      
      final data = jsonDecode(response.body);
      
      // Check if we got valid Reddit data
      if (data == null || data['data'] == null || data['data']['children'] == null) {
        throw Exception('Invalid Reddit API response format');
      }
      
      final List posts = data['data']['children'];
      
      if (posts.isEmpty) {
        if (kDebugMode) {
          print('No Reddit posts found for subreddit: $subreddit');
        }
        return [];
      }
      
      final redditPosts = posts.map((item) {
        final postData = item['data'];
        
        // Validate required fields
        if (postData['title'] == null || postData['title'].toString().isEmpty) {
          return null; // Skip posts without titles
        }
        
        // Skip stickied posts and announcements
        if (postData['stickied'] == true || postData['distinguished'] != null) {
          return null;
        }
        
        // Skip posts with no content and no external links
        final hasContent = postData['selftext'] != null && postData['selftext'].toString().isNotEmpty;
        final hasExternalLink = postData['url'] != null && 
                               postData['url'].toString().startsWith('http') &&
                               !postData['url'].toString().contains('reddit.com');
        
        if (!hasContent && !hasExternalLink) {
          return null; // Skip low-effort posts
        }
        
        // Extract the best available image URL
        String imageUrl = '';
        
        // Check for preview images (highest quality)
        if (postData['preview'] != null && 
            postData['preview']['images'] != null && 
            postData['preview']['images'].isNotEmpty) {
          final previewImage = postData['preview']['images'][0];
          if (previewImage['source'] != null && 
              previewImage['source']['url'] != null) {
            imageUrl = previewImage['source']['url'].toString()
                .replaceAll('&amp;', '&'); // Fix HTML entities
          }
        }
        
        // Fallback to thumbnail if no preview image
        if (imageUrl.isEmpty && 
            postData['thumbnail'] != null && 
            postData['thumbnail'].toString().startsWith('http')) {
          imageUrl = postData['thumbnail'].toString();
        }
        
        // Fallback to external URL if it's an image
        if (imageUrl.isEmpty && 
            postData['url'] != null && 
            postData['url'].toString().startsWith('http') &&
            _isImageUrl(postData['url'].toString())) {
          imageUrl = postData['url'].toString();
        }

        // Create MMA Reddit post
        final mmaPost = MMARedditPost(
          id: postData['id'] ?? '',
          title: postData['title'] ?? '',
          subreddit: postData['subreddit'] ?? subreddit,
          redditAuthor: postData['author'] ?? 'Redditor',
          redditUrl: 'https://www.reddit.com${postData['permalink']}',
          redditScore: (postData['score'] ?? 0).toInt(),
          redditComments: (postData['num_comments'] ?? 0).toInt(),
          redditCreated: DateTime.fromMillisecondsSinceEpoch(
            ((postData['created_utc'] ?? 0) * 1000).toInt(),
          ),
          content: postData['selftext'] ?? '',
          redditThumbnail: imageUrl.isNotEmpty ? imageUrl : null,
          isStickied: postData['stickied'] ?? false,
          isDistinguished: postData['distinguished'] != null,
        );

        // Apply filters if specified
        if (category != null && mmaPost.categorizePost().toString() != 'PostCategory.$category') {
          return null;
        }

        if (fighterName != null && !mmaPost.extractFighterMentions().any((name) => 
            name.toLowerCase().contains(fighterName.toLowerCase()))) {
          return null;
        }

        if (weightClass != null && !mmaPost.content.toLowerCase().contains(weightClass.toLowerCase())) {
          return null;
        }

        return mmaPost;
      }).where((post) => post != null).cast<MMARedditPost>().toList();
      
      if (kDebugMode) {
        print('Fetched ${redditPosts.length} valid MMA Reddit posts from r/$subreddit');
      }
      
      return redditPosts;
      
    } catch (e) {
      if (kDebugMode) {
        print('Error fetching MMA Reddit posts from r/$subreddit: $e');
      }
      // Return empty list instead of throwing to prevent app crashes
      return [];
    }
  }

  /// Fetch posts for a specific fighter
  Future<List<MMARedditPost>> fetchFighterPosts(String fighterName) async {
    List<MMARedditPost> allPosts = [];
    
    // Search across primary subreddits
    for (final subreddit in primarySubreddits) {
      try {
        final posts = await fetchRedditPosts(
          subreddit: subreddit,
          limit: 50, // Get more posts to filter
          fighterName: fighterName,
        );
        allPosts.addAll(posts);
      } catch (e) {
        if (kDebugMode) {
          print('Error fetching fighter posts from r/$subreddit: $e');
        }
      }
    }
    
    // Sort by engagement score and return top posts
    allPosts.sort((a, b) => b.engagementScore.compareTo(a.engagementScore));
    return allPosts.take(20).toList();
  }

  /// Fetch posts for a specific weight class
  Future<List<MMARedditPost>> fetchWeightClassPosts(String weightClass) async {
    List<MMARedditPost> allPosts = [];
    
    for (final subreddit in primarySubreddits) {
      try {
        final posts = await fetchRedditPosts(
          subreddit: subreddit,
          limit: 30,
          weightClass: weightClass,
        );
        allPosts.addAll(posts);
      } catch (e) {
        if (kDebugMode) {
          print('Error fetching weight class posts from r/$subreddit: $e');
        }
      }
    }
    
    allPosts.sort((a, b) => b.engagementScore.compareTo(a.engagementScore));
    return allPosts.take(15).toList();
  }

  /// Fetch posts for a specific category
  Future<List<MMARedditPost>> fetchCategoryPosts(PostCategory category) async {
    List<MMARedditPost> allPosts = [];
    
    for (final subreddit in primarySubreddits) {
      try {
        final posts = await fetchRedditPosts(
          subreddit: subreddit,
          limit: 40,
          category: category.toString().split('.').last,
        );
        allPosts.addAll(posts);
      } catch (e) {
        if (kDebugMode) {
          print('Error fetching category posts from r/$subreddit: $e');
        }
      }
    }
    
    allPosts.sort((a, b) => b.engagementScore.compareTo(a.engagementScore));
    return allPosts.take(20).toList();
  }

  /// Fetch trending posts across all MMA subreddits
  Future<List<MMARedditPost>> fetchTrendingPosts() async {
    List<MMARedditPost> allPosts = [];
    
    for (final subreddit in primarySubreddits) {
      try {
        final posts = await fetchRedditPosts(
          subreddit: subreddit,
          limit: 25,
        );
        allPosts.addAll(posts);
      } catch (e) {
        if (kDebugMode) {
          print('Error fetching trending posts from r/$subreddit: $e');
        }
      }
    }
    
    // Filter for high-quality, recent posts
    allPosts = allPosts.where((post) => 
      post.isHighQuality && post.isRecent
    ).toList();
    
    allPosts.sort((a, b) => b.engagementScore.compareTo(a.engagementScore));
    return allPosts.take(30).toList();
  }

  /// Get subreddit suggestions based on category
  String getSubredditForCategory(PostCategory category) {
    switch (category) {
      case PostCategory.fightResults:
      case PostCategory.fighterNews:
      case PostCategory.championshipNews:
      case PostCategory.fightPredictions:
        return 'ufc';
      case PostCategory.eventDiscussion:
      case PostCategory.trainingContent:
      case PostCategory.behindTheScenes:
        return 'MMA';
      case PostCategory.generalDiscussion:
      case PostCategory.questions:
      case PostCategory.memes:
        return 'MMA';
      default:
        return 'ufc';
    }
  }

  /// Check if URL is an image
  bool _isImageUrl(String url) {
    final imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'];
    final lowerUrl = url.toLowerCase();
    return imageExtensions.any((ext) => lowerUrl.endsWith(ext)) ||
           lowerUrl.contains('imgur.com') ||
           lowerUrl.contains('i.redd.it') ||
           lowerUrl.contains('preview.redd.it');
  }

  /// Filter posts by quality
  List<MMARedditPost> filterQualityPosts(List<MMARedditPost> posts) {
    return posts.where((post) => 
      post.isHighQuality && 
      !post.isStickied && 
      post.content.length > 20
    ).toList();
  }

  /// Calculate post relevance score
  double calculatePostRelevance(MMARedditPost post, String context) {
    double score = 0.0;
    
    // Base engagement score
    score += post.engagementScore * 0.3;
    
    // Recency score
    if (post.isRecent) {
      score += 0.3;
    }
    
    // Content quality score
    if (post.content.length > 100) {
      score += 0.2;
    }
    
    // Context relevance (if fighter name is mentioned)
    if (context.isNotEmpty && 
        post.extractFighterMentions().any((name) => 
            name.toLowerCase().contains(context.toLowerCase()))) {
      score += 0.2;
    }
    
    return score.clamp(0.0, 1.0);
  }
} 