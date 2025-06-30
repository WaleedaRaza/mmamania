class Event {
  final String id;
  final String title;
  final DateTime date;
  final String location;
  final String type; // 'upcoming' or 'past'
  final String? eventUrl;

  Event({
    required this.id,
    required this.title,
    required this.date,
    required this.location,
    required this.type,
    this.eventUrl,
  });

  factory Event.fromJson(Map<String, dynamic> json) {
    return Event(
      id: json['id'] ?? '',
      title: json['title'] ?? '',
      date: json['date'] != null ? DateTime.parse(json['date']) : DateTime.now(),
      location: json['location'] ?? '',
      type: json['type'] ?? 'upcoming',
      eventUrl: json['event_url'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'date': date.toIso8601String(),
      'location': location,
      'type': type,
      'event_url': eventUrl,
    };
  }

  bool get isUpcoming => type == 'upcoming';
  bool get isPast => type == 'past';
  String get displayDate => '${date.month}/${date.day}/${date.year}';
} 