import SwiftUI
import PlaygroundSupport

struct DrawnStroke: Identifiable {
    let id = UUID()
    var points: [CGPoint]
    var color: Color
    var lineWidth: CGFloat
}

struct CanvasDrawingView: View {
    @State private var strokes: [DrawnStroke] = []
    @State private var activeStroke: DrawnStroke?
    @State private var selectedColor: Color = .blue
    @State private var selectedLineWidth: CGFloat = 8

    private let palette: [Color] = [
        .black,
        .blue,
        .pink,
        .orange,
        .green,
        .purple
    ]

    var body: some View {
        VStack(spacing: 20) {
            header
            drawingCanvas
            controls
        }
        .padding(24)
        .frame(width: 430, height: 760)
        .background(
            LinearGradient(
                colors: [Color(red: 0.96, green: 0.97, blue: 1.0), Color(red: 0.91, green: 0.94, blue: 0.98)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        )
    }

    private var header: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text("Canvas Drawing Prototype")
                .font(.system(size: 28, weight: .bold, design: .rounded))
            Text("손가락이나 마우스로 그리면서 색상과 브러시 두께를 바꿔볼 수 있습니다.")
                .font(.system(size: 15, weight: .medium, design: .rounded))
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }

    private var drawingCanvas: some View {
        GeometryReader { geometry in
            ZStack {
                RoundedRectangle(cornerRadius: 28, style: .continuous)
                    .fill(.white.opacity(0.92))
                    .shadow(color: .black.opacity(0.08), radius: 18, x: 0, y: 10)

                RoundedRectangle(cornerRadius: 28, style: .continuous)
                    .stroke(Color.black.opacity(0.06), lineWidth: 1)

                VStack {
                    Spacer()
                    HStack {
                        Spacer()
                        Text("Strokes \(strokes.count)")
                            .font(.system(size: 12, weight: .semibold, design: .rounded))
                            .padding(.horizontal, 10)
                            .padding(.vertical, 6)
                            .background(.ultraThinMaterial, in: Capsule())
                            .padding(18)
                    }
                }

                ForEach(strokes) { stroke in
                    StrokeShape(points: stroke.points)
                        .stroke(stroke.color, style: StrokeStyle(lineWidth: stroke.lineWidth, lineCap: .round, lineJoin: .round))
                }

                if let activeStroke {
                    StrokeShape(points: activeStroke.points)
                        .stroke(activeStroke.color, style: StrokeStyle(lineWidth: activeStroke.lineWidth, lineCap: .round, lineJoin: .round))
                }
            }
            .contentShape(RoundedRectangle(cornerRadius: 28, style: .continuous))
            .gesture(
                DragGesture(minimumDistance: 0)
                    .onChanged { value in
                        let point = value.location.clamped(to: geometry.size)

                        if activeStroke == nil {
                            activeStroke = DrawnStroke(
                                points: [point],
                                color: selectedColor,
                                lineWidth: selectedLineWidth
                            )
                        } else {
                            activeStroke?.points.append(point)
                        }
                    }
                    .onEnded { _ in
                        guard let activeStroke, !activeStroke.points.isEmpty else {
                            self.activeStroke = nil
                            return
                        }

                        strokes.append(activeStroke)
                        self.activeStroke = nil
                    }
            )
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }

    private var controls: some View {
        VStack(spacing: 16) {
            HStack {
                Text("Color")
                    .font(.system(size: 15, weight: .bold, design: .rounded))
                Spacer()
                HStack(spacing: 12) {
                    ForEach(Array(palette.enumerated()), id: \.offset) { _, color in
                        Button {
                            selectedColor = color
                        } label: {
                            Circle()
                                .fill(color)
                                .frame(width: 28, height: 28)
                                .overlay(
                                    Circle()
                                        .stroke(.white, lineWidth: 2)
                                        .padding(4)
                                        .opacity(selectedColor == color ? 1 : 0)
                                )
                                .shadow(color: .black.opacity(0.12), radius: 6, x: 0, y: 4)
                        }
                        .buttonStyle(.plain)
                    }
                }
            }

            VStack(alignment: .leading, spacing: 10) {
                HStack {
                    Text("Brush")
                        .font(.system(size: 15, weight: .bold, design: .rounded))
                    Spacer()
                    Text("\(Int(selectedLineWidth)) pt")
                        .font(.system(size: 14, weight: .semibold, design: .rounded))
                        .foregroundStyle(.secondary)
                }

                Slider(value: $selectedLineWidth, in: 2...24, step: 1)
                    .tint(selectedColor)
            }

            HStack(spacing: 12) {
                Button {
                    if !strokes.isEmpty {
                        _ = strokes.removeLast()
                    }
                } label: {
                    Label("Undo", systemImage: "arrow.uturn.backward")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(PrototypeButtonStyle(tint: Color(red: 0.17, green: 0.43, blue: 0.79)))

                Button {
                    strokes.removeAll()
                    activeStroke = nil
                } label: {
                    Label("Clear", systemImage: "trash")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(PrototypeButtonStyle(tint: Color(red: 0.86, green: 0.32, blue: 0.25)))
            }
        }
        .padding(20)
        .background(.white.opacity(0.78), in: RoundedRectangle(cornerRadius: 24, style: .continuous))
    }
}

struct StrokeShape: Shape {
    var points: [CGPoint]

    func path(in rect: CGRect) -> Path {
        var path = Path()

        guard let first = points.first else {
            return path
        }

        path.move(to: first)

        if points.count == 1 {
            path.addEllipse(in: CGRect(x: first.x - 0.5, y: first.y - 0.5, width: 1, height: 1))
            return path
        }

        for point in points.dropFirst() {
            path.addLine(to: point)
        }

        return path
    }
}

struct PrototypeButtonStyle: ButtonStyle {
    var tint: Color

    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(.system(size: 15, weight: .bold, design: .rounded))
            .padding(.horizontal, 16)
            .padding(.vertical, 14)
            .background(tint.opacity(configuration.isPressed ? 0.75 : 1), in: RoundedRectangle(cornerRadius: 18, style: .continuous))
            .foregroundStyle(.white)
            .scaleEffect(configuration.isPressed ? 0.98 : 1)
            .animation(.easeOut(duration: 0.16), value: configuration.isPressed)
    }
}

extension CGPoint {
    func clamped(to size: CGSize) -> CGPoint {
        CGPoint(
            x: min(max(0, x), size.width),
            y: min(max(0, y), size.height)
        )
    }
}

PlaygroundPage.current.setLiveView(CanvasDrawingView())