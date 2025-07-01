import 'package:flutter/foundation.dart';

enum PostCategory {
  fightResults,
  fighterNews,
  eventDiscussion,
  trainingContent,
  championshipNews,
  fightPredictions,
  behindTheScenes,
  generalDiscussion,
  memes,
  questions,
}

enum PostStatus {
  pending,
  approved,
  rejected,
  flagged,
}

class Comment {
  final String id;
  final String content;
  final String author;
  final DateTime createdAt;
  final int upvotes;
  final List<Comment> replies;

  Comment({
    required this.id,
    required this.content,
    required this.author,
    required this.createdAt,
    this.upvotes = 0,
    this.replies = const [],
  });

  factory Comment.fromJson(Map<String, dynamic> json) {
    return Comment(
      id: json['id'] as String,
      content: json['content'] as String,
      author: json['author'] as String,
      createdAt: DateTime.parse(json['createdAt'] as String),
      upvotes: json['upvotes'] as int? ?? 0,
      replies: (json['replies'] as List<dynamic>?)
          ?.map((r) => Comment.fromJson(r as Map<String, dynamic>))
          .toList() ?? [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'content': content,
      'author': author,
      'createdAt': createdAt.toIso8601String(),
      'upvotes': upvotes,
      'replies': replies.map((r) => r.toJson()).toList(),
    };
  }
}

class MMAPost {
  final String id;
  final String title;
  final String content;
  final String author;
  final String? imageUrl;
  final int upvotes;
  final DateTime createdAt;
  final String postType;
  final String? redditUrl;
  final List<Comment> comments;
  final String? fighterId;
  final String? eventId;
  final String? weightClass;
  final String? fightResult;
  final List<String> tags;
  final PostCategory category;
  final PostStatus status;

  MMAPost({
    required this.id,
    required this.title,
    required this.content,
    required this.author,
    this.imageUrl,
    this.upvotes = 0,
    required this.createdAt,
    required this.postType,
    this.redditUrl,
    this.comments = const [],
    this.fighterId,
    this.eventId,
    this.weightClass,
    this.fightResult,
    this.tags = const [],
    this.category = PostCategory.generalDiscussion,
    this.status = PostStatus.approved,
  });

  factory MMAPost.fromJson(Map<String, dynamic> json) {
    return MMAPost(
      id: json['id']?.toString() ?? '',
      title: json['title'] as String? ?? '',
      content: json['content'] as String? ?? '',
      author: json['author'] as String? ?? '',
      imageUrl: json['imageUrl'] as String?,
      upvotes: json['upvotes'] as int? ?? 0,
      createdAt: DateTime.tryParse(json['createdAt'] as String? ?? '') ?? DateTime.now(),
      postType: json['postType'] as String? ?? '',
      redditUrl: json['redditUrl'] as String?,
      comments: (json['comments'] as List<dynamic>?)
          ?.map((c) => Comment.fromJson(c as Map<String, dynamic>))
          .toList() ?? [],
      fighterId: json['fighterId'] as String?,
      eventId: json['eventId'] as String?,
      weightClass: json['weightClass'] as String?,
      fightResult: json['fightResult'] as String?,
      tags: (json['tags'] as List<dynamic>?)?.cast<String>() ?? [],
      category: PostCategory.values.firstWhere(
        (e) => e.toString() == 'PostCategory.${json['category']}',
        orElse: () => PostCategory.generalDiscussion,
      ),
      status: PostStatus.values.firstWhere(
        (e) => e.toString() == 'PostStatus.${json['status']}',
        orElse: () => PostStatus.approved,
      ),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'content': content,
      'author': author,
      'imageUrl': imageUrl,
      'upvotes': upvotes,
      'createdAt': createdAt.toIso8601String(),
      'postType': postType,
      'redditUrl': redditUrl,
      'comments': comments.map((c) => c.toJson()).toList(),
      'fighterId': fighterId,
      'eventId': eventId,
      'weightClass': weightClass,
      'fightResult': fightResult,
      'tags': tags,
      'category': category.toString().split('.').last,
      'status': status.toString().split('.').last,
    };
  }

  MMAPost copyWith({
    String? id,
    String? title,
    String? content,
    String? author,
    String? imageUrl,
    int? upvotes,
    DateTime? createdAt,
    String? postType,
    String? redditUrl,
    List<Comment>? comments,
    String? fighterId,
    String? eventId,
    String? weightClass,
    String? fightResult,
    List<String>? tags,
    PostCategory? category,
    PostStatus? status,
  }) {
    return MMAPost(
      id: id ?? this.id,
      title: title ?? this.title,
      content: content ?? this.content,
      author: author ?? this.author,
      imageUrl: imageUrl ?? this.imageUrl,
      upvotes: upvotes ?? this.upvotes,
      createdAt: createdAt ?? this.createdAt,
      postType: postType ?? this.postType,
      redditUrl: redditUrl ?? this.redditUrl,
      comments: comments ?? this.comments,
      fighterId: fighterId ?? this.fighterId,
      eventId: eventId ?? this.eventId,
      weightClass: weightClass ?? this.weightClass,
      fightResult: fightResult ?? this.fightResult,
      tags: tags ?? this.tags,
      category: category ?? this.category,
      status: status ?? this.status,
    );
  }
} 