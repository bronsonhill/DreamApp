//
//  ContentView.swift
//  Dream
//
//  Created by Bronson Hill on 29/5/2023.
//

import SwiftUI

struct ContentView: View {
    @State var authorInfo: String = ""
    var body: some View {
        VStack {
            Image(systemName: "globe")
                .imageScale(.large)
                .foregroundColor(.accentColor)
            Text("Hello, world!")
            TextField("What kind of books do you like to read?", text: $authorInfo)
                .padding(.horizontal, 100.00)
            
        }
        .textFieldStyle(.roundedBorder)
        .padding()
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
