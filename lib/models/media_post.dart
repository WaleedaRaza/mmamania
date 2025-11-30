import 'package:flutter/material.dart';

class MediaPost {
  final String id;
  final String platform; // 'youtube', 'twitter', 'reddit', 'tiktok'
  final String url;
  final String title;
  final String description;
  final String? thumbnailUrl;
  final String authorName;
  final String? authorHandle;
  final bool? authorVerified;
  final DateTime publishedAt;
  final int viewCount;
  final int likeCount;
  final int? shareCount;
  final int? commentCount;
  final String contentType; // 'highlight', 'interview', 'news', 'analysis', 'event'
  final int? durationSeconds;
  final int relevanceScore;
  final int sourcePriority;
  final double? contextualScore;
  
  MediaPost({
    required this.id,
    required this.platform,
    required this.url,
    required this.title,
    required this.description,
    this.thumbnailUrl,
    required this.authorName,
    this.authorHandle,
    this.authorVerified,
    required this.publishedAt,
    this.viewCount = 0,
    this.likeCount = 0,
    this.shareCount,
    this.commentCount,
    this.contentType = 'general',
    this.durationSeconds,
    this.relevanceScore = 0,
    this.sourcePriority = 1,
    this.contextualScore,
  });
  
  factory MediaPost.fromJson(Map<String, dynamic> json) {
    return MediaPost(
      id: json['platform_id'] ?? json['id'] ?? '',
      platform: json['platform'] ?? 'unknown',
      url: json['url'] ?? '',
      title: json['title'] ?? '',
      description: json['description'] ?? '',
      thumbnailUrl: json['thumbnail_url'],
      authorName: json['author_name'] ?? '',
      authorHandle: json['author_handle'],
      authorVerified: json['author_verified'],
      publishedAt: DateTime.parse(json['published_at']),
      viewCount: json['view_count'] ?? 0,
      likeCount: json['like_count'] ?? 0,
      shareCount: json['share_count'],
      commentCount: json['comment_count'],
      contentType: json['content_type'] ?? 'general',
      durationSeconds: json['duration_seconds'],
      relevanceScore: json['relevance_score'] ?? 0,
      sourcePriority: json['source_priority'] ?? 1,
      contextualScore: json['contextual_score']?.toDouble(),
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'platform': platform,
      'url': url,
      'title': title,
      'description': description,
      'thumbnail_url': thumbnailUrl,
      'author_name': authorName,
      'author_handle': authorHandle,
      'author_verified': authorVerified,
      'published_at': publishedAt.toIso8601String(),
      'view_count': viewCount,
      'like_count': likeCount,
      'share_count': shareCount,
      'comment_count': commentCount,
      'content_type': contentType,
      'duration_seconds': durationSeconds,
      'relevance_score': relevanceScore,
      'source_priority': sourcePriority,
      'contextual_score': contextualScore,
    };
  }
  
  String get formattedDuration {
    if (durationSeconds == null || durationSeconds == 0) return '';
    
    final minutes = durationSeconds! ~/ 60;
    final seconds = durationSeconds! % 60;
    
    if (minutes >= 60) {
      final hours = minutes ~/ 60;
      final remainingMinutes = minutes % 60;
      return '${hours}:${remainingMinutes.toString().padLeft(2, '0')}:${seconds.toString().padLeft(2, '0')}';
    }
    
    return '${minutes}:${seconds.toString().padLeft(2, '0')}';
  }
  
  String get formattedViewCount {
    if (viewCount >= 1000000) {
      return '${(viewCount / 1000000).toStringAsFixed(1)}M';
    } else if (viewCount >= 1000) {
      return '${(viewCount / 1000).toStringAsFixed(1)}K';
    }
    return viewCount.toString();
  }
  
  String get formattedLikeCount {
    if (likeCount >= 1000000) {
      return '${(likeCount / 1000000).toStringAsFixed(1)}M';
    } else if (likeCount >= 1000) {
      return '${(likeCount / 1000).toStringAsFixed(1)}K';
    }
    return likeCount.toString();
  }
  
  String get timeAgo {
    final now = DateTime.now();
    final difference = now.difference(publishedAt);
    
    if (difference.inDays > 0) {
      return '${difference.inDays}d ago';
    } else if (difference.inHours > 0) {
      return '${difference.inHours}h ago';
    } else if (difference.inMinutes > 0) {
      return '${difference.inMinutes}m ago';
    } else {
      return 'Just now';
    }
  }
  
  String get platformIcon {
    switch (platform.toLowerCase()) {
      case 'youtube':
        return '🎥';
      case 'twitter':
        return '🐦';
      case 'tiktok':
        return '🎵';
      case 'reddit':
        return '🤖';
      default:
        return '📱';
    }
  }
  
  String get contentTypeIcon {
    switch (contentType.toLowerCase()) {
      case 'highlights':
        return '⚡';
      case 'interview':
        return '🎤';
      case 'news':
        return '📰';
      case 'analysis':
        return '📊';
      case 'event':
        return '🎪';
      case 'podcast':
        return '🎧';
      default:
        return '📄';
    }
  }
  
  Color get contentTypeColor {
    switch (contentType.toLowerCase()) {
      case 'highlights':
        return Colors.orange;
      case 'interview':
        return Colors.blue;
      case 'news':
        return Colors.red;
      case 'analysis':
        return Colors.purple;
      case 'event':
        return Colors.green;
      case 'podcast':
        return Colors.teal;
      default:
        return Colors.grey;
    }
  }
}



