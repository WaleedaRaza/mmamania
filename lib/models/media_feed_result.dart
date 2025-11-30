import 'media_post.dart';

class SearchContext {
  final String? eventName;
  final List<String>? fighterNames;
  final int searchTermsUsed;
  
  SearchContext({
    this.eventName,
    this.fighterNames,
    required this.searchTermsUsed,
  });
  
  factory SearchContext.fromJson(Map<String, dynamic> json) {
    return SearchContext(
      eventName: json['event_name'],
      fighterNames: (json['fighter_names'] as List<dynamic>?)
          ?.map((name) => name.toString())
          .toList(),
      searchTermsUsed: json['search_terms_used'] ?? 0,
    );
  }
}

class MediaFeedResult {
  final int totalContent;
  final int youtubeCount;
  final int twitterCount;
  final int tiktokCount;
  final List<MediaPost> content;
  final SearchContext? searchContext;
  final DateTime scrapedAt;
  final String? error;
  
  MediaFeedResult({
    required this.totalContent,
    required this.youtubeCount,
    required this.twitterCount,
    required this.tiktokCount,
    required this.content,
    this.searchContext,
    required this.scrapedAt,
    this.error,
  });
  
  factory MediaFeedResult.fromJson(Map<String, dynamic> json) {
    return MediaFeedResult(
      totalContent: json['total_content'] ?? 0,
      youtubeCount: json['youtube_count'] ?? 0,
      twitterCount: json['twitter_count'] ?? 0,
      tiktokCount: json['tiktok_count'] ?? 0,
      content: (json['content'] as List<dynamic>?)
          ?.map((item) => MediaPost.fromJson(item))
          .toList() ?? [],
      searchContext: json['search_context'] != null 
          ? SearchContext.fromJson(json['search_context'])
          : null,
      scrapedAt: DateTime.parse(json['scraped_at']),
      error: json['error'],
    );
  }
  
  bool get hasError => error != null;
  
  bool get isEmpty => content.isEmpty;
  
  List<MediaPost> get youtubeContent => 
      content.where((post) => post.platform == 'youtube').toList();
  
  List<MediaPost> get twitterContent => 
      content.where((post) => post.platform == 'twitter').toList();
  
  List<MediaPost> get tiktokContent => 
      content.where((post) => post.platform == 'tiktok').toList();
  
  List<MediaPost> get redditContent => 
      content.where((post) => post.platform == 'reddit').toList();
  
  List<MediaPost> getByContentType(String contentType) =>
      content.where((post) => post.contentType.toLowerCase() == contentType.toLowerCase()).toList();
  
  List<MediaPost> getHighPriorityContent() =>
      content.where((post) => post.sourcePriority >= 4).toList();
  
  List<MediaPost> getRecentContent({int hours = 24}) {
    final cutoff = DateTime.now().subtract(Duration(hours: hours));
    return content.where((post) => post.publishedAt.isAfter(cutoff)).toList();
  }
}
