import 'mma_post.dart';

class MMARedditPost extends MMAPost {
  final String subreddit;
  final String redditUrl;
  final int redditScore;
  final int redditComments;
  final String redditAuthor;
  final DateTime redditCreated;
  final String? redditThumbnail;
  final bool isStickied;
  final bool isDistinguished;

  MMARedditPost({
    required String id,
    required String title,
    required String subreddit,
    required String redditAuthor,
    required String redditUrl,
    required this.redditScore,
    required this.redditComments,
    required this.redditCreated,
    required String content,
    String? redditThumbnail,
    this.isStickied = false,
    this.isDistinguished = false,
    String? fighterId,
    String? eventId,
    String? weightClass,
    String? fightResult,
    List<String> tags = const [],
    PostCategory category = PostCategory.generalDiscussion,
  })  : subreddit = subreddit,
        redditUrl = redditUrl,
        redditAuthor = redditAuthor,
        redditThumbnail = redditThumbnail,
        super(
          id: id,
          title: title,
          content: content,
          author: redditAuthor,
          imageUrl: redditThumbnail,
          upvotes: redditScore,
          createdAt: redditCreated,
          postType: 'reddit',
          redditUrl: redditUrl,
          fighterId: fighterId,
          eventId: eventId,
          weightClass: weightClass,
          fightResult: fightResult,
          tags: tags,
          category: category,
        );

  factory MMARedditPost.fromJson(Map<String, dynamic> json) {
    return MMARedditPost(
      id: json['id'] as String,
      title: json['title'] as String,
      subreddit: json['subreddit'] as String,
      redditAuthor: json['redditAuthor'] as String,
      redditUrl: json['redditUrl'] as String,
      redditScore: json['redditScore'] as int,
      redditComments: json['redditComments'] as int,
      redditCreated: DateTime.parse(json['redditCreated'] as String),
      content: json['content'] as String,
      redditThumbnail: json['redditThumbnail'] as String?,
      isStickied: json['isStickied'] as bool? ?? false,
      isDistinguished: json['isDistinguished'] as bool? ?? false,
      fighterId: json['fighterId'] as String?,
      eventId: json['eventId'] as String?,
      weightClass: json['weightClass'] as String?,
      fightResult: json['fightResult'] as String?,
      tags: (json['tags'] as List<dynamic>?)?.cast<String>() ?? [],
      category: PostCategory.values.firstWhere(
        (e) => e.toString() == 'PostCategory.${json['category']}',
        orElse: () => PostCategory.generalDiscussion,
      ),
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      ...super.toJson(),
      'subreddit': subreddit,
      'redditScore': redditScore,
      'redditComments': redditComments,
      'redditAuthor': redditAuthor,
      'redditCreated': redditCreated.toIso8601String(),
      'redditThumbnail': redditThumbnail,
      'isStickied': isStickied,
      'isDistinguished': isDistinguished,
    };
  }

  // Helper methods for content analysis
  bool get isHighQuality {
    return redditScore > 10 && redditComments > 5 && content.length > 50;
  }

  bool get isRecent {
    final daysSinceCreated = DateTime.now().difference(redditCreated).inDays;
    return daysSinceCreated <= 7;
  }

  double get engagementScore {
    return (redditScore * 0.6) + (redditComments * 0.4);
  }

  // Extract fighter mentions from content
  List<String> extractFighterMentions() {
    // This is a simple implementation - could be enhanced with NLP
    final commonFighterNames = [
      'McGregor', 'Khabib', 'Jones', 'Adesanya', 'Usman', 'Volkanovski',
      'Makhachev', 'Pantoja', 'O\'Malley', 'Edwards', 'Pereira', 'Hill',
      'Moreno', 'Figueiredo', 'Sterling', 'Yan', 'Oliveira', 'Chandler',
      'Poirier', 'Gaethje', 'Whittaker', 'Costa', 'Vettori', 'Cannonier',
    ];

    final mentions = <String>[];
    final contentLower = content.toLowerCase();
    final titleLower = title.toLowerCase();

    for (final name in commonFighterNames) {
      if (contentLower.contains(name.toLowerCase()) || 
          titleLower.contains(name.toLowerCase())) {
        mentions.add(name);
      }
    }

    return mentions;
  }

  // Categorize post based on content
  PostCategory categorizePost() {
    final contentLower = content.toLowerCase();
    final titleLower = title.toLowerCase();

    if (titleLower.contains('results') || contentLower.contains('won') || contentLower.contains('defeated')) {
      return PostCategory.fightResults;
    }
    if (titleLower.contains('vs') || titleLower.contains('fight') || contentLower.contains('fight')) {
      return PostCategory.fightPredictions;
    }
    if (titleLower.contains('champion') || titleLower.contains('title') || contentLower.contains('belt')) {
      return PostCategory.championshipNews;
    }
    if (titleLower.contains('training') || contentLower.contains('training') || contentLower.contains('camp')) {
      return PostCategory.trainingContent;
    }
    if (titleLower.contains('event') || titleLower.contains('ufc') || contentLower.contains('card')) {
      return PostCategory.eventDiscussion;
    }
    if (titleLower.contains('behind') || titleLower.contains('scenes') || contentLower.contains('backstage')) {
      return PostCategory.behindTheScenes;
    }
    if (titleLower.contains('?') || titleLower.contains('question') || contentLower.contains('?')) {
      return PostCategory.questions;
    }

    return PostCategory.generalDiscussion;
  }
} 