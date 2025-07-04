class User {
  final String id;
  final String username;
  final String email;
  final String? profilePicture;
  final DateTime createdAt;
  final DateTime updatedAt;
  final UserPreferences preferences;
  final List<String> favoriteFighters;
  final String? goatFighter;
  final List<HotTake> hotTakes;
  final UserStats stats;

  User({
    required this.id,
    required this.username,
    required this.email,
    this.profilePicture,
    required this.createdAt,
    required this.updatedAt,
    required this.preferences,
    this.favoriteFighters = const [],
    this.goatFighter,
    this.hotTakes = const [],
    required this.stats,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      username: json['username'],
      email: json['email'],
      profilePicture: json['profile_picture'],
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
      preferences: UserPreferences.fromJson(json['preferences'] ?? {}),
      favoriteFighters: (json['favorite_fighters'] as List<dynamic>?)?.cast<String>() ?? [],
      goatFighter: json['goat_fighter'],
      hotTakes: (json['hot_takes'] as List<dynamic>?)
          ?.map((e) => HotTake.fromJson(e))
          .toList() ?? [],
      stats: UserStats.fromJson(json['stats'] ?? {}),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'username': username,
      'email': email,
      'profile_picture': profilePicture,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
      'preferences': preferences.toJson(),
      'favorite_fighters': favoriteFighters,
      'goat_fighter': goatFighter,
      'hot_takes': hotTakes.map((e) => e.toJson()).toList(),
      'stats': stats.toJson(),
    };
  }

  User copyWith({
    String? id,
    String? username,
    String? email,
    String? profilePicture,
    DateTime? createdAt,
    DateTime? updatedAt,
    UserPreferences? preferences,
    List<String>? favoriteFighters,
    String? goatFighter,
    List<HotTake>? hotTakes,
    UserStats? stats,
  }) {
    return User(
      id: id ?? this.id,
      username: username ?? this.username,
      email: email ?? this.email,
      profilePicture: profilePicture ?? this.profilePicture,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      preferences: preferences ?? this.preferences,
      favoriteFighters: favoriteFighters ?? this.favoriteFighters,
      goatFighter: goatFighter ?? this.goatFighter,
      hotTakes: hotTakes ?? this.hotTakes,
      stats: stats ?? this.stats,
    );
  }

  bool get isProfileComplete => 
      favoriteFighters.length >= 5 && 
      goatFighter != null && 
      hotTakes.isNotEmpty;

  @override
  String toString() {
    return 'User(id: $id, username: $username, email: $email)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is User && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
}

class UserPreferences {
  final bool notificationsEnabled;
  final bool emailNotifications;
  final String theme;
  final String language;
  final bool autoJoinAudio;
  final bool showOnlineStatus;

  UserPreferences({
    this.notificationsEnabled = true,
    this.emailNotifications = true,
    this.theme = 'dark',
    this.language = 'en',
    this.autoJoinAudio = false,
    this.showOnlineStatus = true,
  });

  factory UserPreferences.fromJson(Map<String, dynamic> json) {
    return UserPreferences(
      notificationsEnabled: json['notifications_enabled'] ?? true,
      emailNotifications: json['email_notifications'] ?? true,
      theme: json['theme'] ?? 'dark',
      language: json['language'] ?? 'en',
      autoJoinAudio: json['auto_join_audio'] ?? false,
      showOnlineStatus: json['show_online_status'] ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'notifications_enabled': notificationsEnabled,
      'email_notifications': emailNotifications,
      'theme': theme,
      'language': language,
      'auto_join_audio': autoJoinAudio,
      'show_online_status': showOnlineStatus,
    };
  }
}

class HotTake {
  final String id;
  final String title;
  final String description;
  final DateTime createdAt;
  final int upvotes;
  final int downvotes;
  final bool isControversial;

  HotTake({
    required this.id,
    required this.title,
    required this.description,
    required this.createdAt,
    this.upvotes = 0,
    this.downvotes = 0,
    this.isControversial = false,
  });

  factory HotTake.fromJson(Map<String, dynamic> json) {
    return HotTake(
      id: json['id'],
      title: json['title'],
      description: json['description'],
      createdAt: DateTime.parse(json['created_at']),
      upvotes: json['upvotes'] ?? 0,
      downvotes: json['downvotes'] ?? 0,
      isControversial: json['is_controversial'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'description': description,
      'created_at': createdAt.toIso8601String(),
      'upvotes': upvotes,
      'downvotes': downvotes,
      'is_controversial': isControversial,
    };
  }

  int get score => upvotes - downvotes;
}

class UserStats {
  final int debatesJoined;
  final int debatesHosted;
  final int totalSpeakingTime;
  final int hotTakesCreated;
  final int totalUpvotes;
  final int totalDownvotes;
  final int followers;
  final int following;
  final DateTime lastActive;

  UserStats({
    this.debatesJoined = 0,
    this.debatesHosted = 0,
    this.totalSpeakingTime = 0,
    this.hotTakesCreated = 0,
    this.totalUpvotes = 0,
    this.totalDownvotes = 0,
    this.followers = 0,
    this.following = 0,
    required this.lastActive,
  });

  factory UserStats.fromJson(Map<String, dynamic> json) {
    return UserStats(
      debatesJoined: json['debates_joined'] ?? 0,
      debatesHosted: json['debates_hosted'] ?? 0,
      totalSpeakingTime: json['total_speaking_time'] ?? 0,
      hotTakesCreated: json['hot_takes_created'] ?? 0,
      totalUpvotes: json['total_upvotes'] ?? 0,
      totalDownvotes: json['total_downvotes'] ?? 0,
      followers: json['followers'] ?? 0,
      following: json['following'] ?? 0,
      lastActive: DateTime.parse(json['last_active']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'debates_joined': debatesJoined,
      'debates_hosted': debatesHosted,
      'total_speaking_time': totalSpeakingTime,
      'hot_takes_created': hotTakesCreated,
      'total_upvotes': totalUpvotes,
      'total_downvotes': totalDownvotes,
      'followers': followers,
      'following': following,
      'last_active': lastActive.toIso8601String(),
    };
  }

  int get totalScore => totalUpvotes - totalDownvotes;
  String get formattedSpeakingTime {
    final hours = totalSpeakingTime ~/ 3600;
    final minutes = (totalSpeakingTime % 3600) ~/ 60;
    if (hours > 0) {
      return '${hours}h ${minutes}m';
    }
    return '${minutes}m';
  }
} 