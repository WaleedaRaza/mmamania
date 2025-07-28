import 'fight.dart';

class Event {
  final String id;
  final String title;
  final DateTime date; // Change from DateTime? to DateTime
  final List<Fight> fights;
  final String eventUrl;
  final String? location;
  final String? venue;
  final String? broadcastInfo;
  final String? mainEventTitle;
  final String? coMainEventTitle;
  final bool isUpcoming;
  final String type; // Add type property for filtering

  Event({
    required this.id,
    required this.title,
    required this.date,
    required this.fights,
    required this.eventUrl,
    this.location,
    this.venue,
    this.broadcastInfo,
    this.mainEventTitle,
    this.coMainEventTitle,
    this.isUpcoming = false,
    this.type = 'upcoming', // Default to upcoming
  });

  String get displayDate {
    return '${date.day}/${date.month}/${date.year}'; // Remove null check since date is now non-nullable
  }

  factory Event.fromJson(Map<String, dynamic> json) => Event(
    id: json['id'] ?? '',
    title: json['title'],
    date: DateTime.parse(json['date']), // Remove null check since date is now non-nullable
    fights: (json['fights'] as List).map((f) => Fight.fromJson(f)).toList(),
    eventUrl: json['eventUrl'],
    location: json['location'],
    venue: json['venue'],
    broadcastInfo: json['broadcastInfo'],
    mainEventTitle: json['mainEventTitle'],
    coMainEventTitle: json['coMainEventTitle'],
    isUpcoming: json['isUpcoming'] ?? false,
    type: json['type'] ?? 'upcoming', // Add type parsing
  );

  Map<String, dynamic> toJson() => {
    'id': id,
    'title': title,
    'date': date.toIso8601String(), // Remove null check since date is now non-nullable
    'fights': fights.map((f) => f.toJson()).toList(),
    'eventUrl': eventUrl,
    'location': location,
    'venue': venue,
    'broadcastInfo': broadcastInfo,
    'mainEventTitle': mainEventTitle,
    'coMainEventTitle': coMainEventTitle,
    'isUpcoming': isUpcoming,
    'type': type, // Add type to toJson
  };
} 