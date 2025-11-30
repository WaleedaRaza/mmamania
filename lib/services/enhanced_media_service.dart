import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/media_feed_result.dart';
import '../models/media_post.dart';

class EnhancedMediaService {
  static const String baseUrl = 'http://localhost:8000';
  
  Future<MediaFeedResult> fetchComprehensiveContent({
    String? eventName,
    List<String>? fighterNames,
    int maxPerPlatform = 25,
  }) async {
    try {
      final queryParams = <String, String>{
        'max_per_platform': maxPerPlatform.toString(),
      };
      
      if (eventName != null) {
        queryParams['event_name'] = eventName;
      }
      
      if (fighterNames != null && fighterNames.isNotEmpty) {
        queryParams['fighter_names'] = fighterNames.join(',');
      }
      
      final uri = Uri.parse('$baseUrl/api/media/scrape-comprehensive')
          .replace(queryParameters: queryParams);
      
      final response = await http.get(
        uri,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return MediaFeedResult.fromJson(data);
      } else {
        throw Exception('Failed to fetch content: ${response.statusCode}');
      }
    } catch (e) {
      print('Enhanced media service error: $e');
      throw Exception('Network error: $e');
    }
  }
  
  Future<List<MediaPost>> fetchByPlatform({
    required String platform,
    String? searchTerms,
    int limit = 20,
  }) async {
    try {
      final queryParams = <String, String>{
        'limit': limit.toString(),
      };
      
      if (searchTerms != null) {
        queryParams['search_terms'] = searchTerms;
      }
      
      final uri = Uri.parse('$baseUrl/api/media/scrape-by-platform/$platform')
          .replace(queryParameters: queryParams);
      
      final response = await http.get(
        uri,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return (data['content'] as List<dynamic>)
            .map((item) => MediaPost.fromJson(item))
            .toList();
      } else {
        throw Exception('Failed to fetch $platform content: ${response.statusCode}');
      }
    } catch (e) {
      print('Platform media service error: $e');
      throw Exception('Network error: $e');
    }
  }
  
  Future<Map<String, dynamic>> getSearchTerms({
    String? eventName,
    List<String>? fighterNames,
  }) async {
    try {
      final queryParams = <String, String>{};
      
      if (eventName != null) {
        queryParams['event_name'] = eventName;
      }
      
      if (fighterNames != null && fighterNames.isNotEmpty) {
        queryParams['fighter_names'] = fighterNames.join(',');
      }
      
      final uri = Uri.parse('$baseUrl/api/media/search-terms')
          .replace(queryParameters: queryParams);
      
      final response = await http.get(
        uri,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      );
      
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to get search terms: ${response.statusCode}');
      }
    } catch (e) {
      print('Search terms service error: $e');
      throw Exception('Network error: $e');
    }
  }
  
  // Convenience methods for specific platforms
  Future<List<MediaPost>> fetchYouTubeContent({
    String? searchTerms,
    int limit = 20,
  }) async {
    return fetchByPlatform(
      platform: 'youtube',
      searchTerms: searchTerms,
      limit: limit,
    );
  }
  
  Future<List<MediaPost>> fetchTwitterContent({
    String? searchTerms,
    int limit = 20,
  }) async {
    return fetchByPlatform(
      platform: 'twitter',
      searchTerms: searchTerms,
      limit: limit,
    );
  }
  
  Future<List<MediaPost>> fetchTikTokContent({
    String? searchTerms,
    int limit = 20,
  }) async {
    return fetchByPlatform(
      platform: 'tiktok',
      searchTerms: searchTerms,
      limit: limit,
    );
  }
  
  // Event-specific content fetching
  Future<MediaFeedResult> fetchEventContent(String eventName) async {
    return fetchComprehensiveContent(
      eventName: eventName,
      maxPerPlatform: 30,
    );
  }
  
  // Fighter-specific content fetching
  Future<MediaFeedResult> fetchFighterContent(List<String> fighterNames) async {
    return fetchComprehensiveContent(
      fighterNames: fighterNames,
      maxPerPlatform: 20,
    );
  }
  
  // Trending content (no specific context)
  Future<MediaFeedResult> fetchTrendingContent() async {
    return fetchComprehensiveContent(
      maxPerPlatform: 15,
    );
  }
}
