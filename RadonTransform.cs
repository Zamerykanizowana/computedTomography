using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace Tomograph
{
    public class RadonTransform
    {

        public Bitmap InBitmap;

        public Bitmap Sinogram;
        public int[,] SinogramValues;
        // nowa tablica do rozmania

        public int Scans;
        public int Detectors;
        public int BeamExtend;

        public RadonTransform(Bitmap inBitmap, int scans, int detectors, int beamExtend)
        {
            this.InBitmap = inBitmap;
            this.Scans = scans;
            this.Detectors = detectors;
            this.BeamExtend = beamExtend;
            SinogramValues = new int[scans, detectors];
        }

        public Bitmap CreateOutImage(int iteration)
        {
            Bitmap outBitmap = new Bitmap(InBitmap.Width,InBitmap.Height);

            for (int i = 0; i < InBitmap.Width; i++)
            {
                for (int j = 0; j < InBitmap.Height; j++)
                {
                      outBitmap.SetPixel(i,j, Color.FromArgb(0,0,0));
                }
            }

            int r = InBitmap.Width > InBitmap.Height ? InBitmap.Width / 2 : InBitmap.Height / 2;
            double angle = 360 / (double)Scans;

            int count = 0;
            for (double alfa = 0; alfa < iteration*angle; alfa = alfa + angle)
            {
                //x,y - Emiter
                int eX = (int)(r * Math.Cos(GetRadians(alfa)));
                int eY = (int)(r * Math.Sin(GetRadians(alfa)));

                //x,y - D0 
                int dX = (int)(r * Math.Cos(GetRadians(alfa) + Math.PI - (GetRadians(BeamExtend) / 2)));
                int dY = (int)(r * Math.Sin(GetRadians(alfa) + Math.PI - (GetRadians(BeamExtend) / 2)));

                //Przy wyszukiwaniu punktów dodajemy do x i y "r", bo wzór jest ustawiony tak, że środek koła
                // znajduje się w punkcie (0,0). Dodając "r" przenosimy się w przestrzeń bitmapy tj. tylko pierwsza ćwiartka układu
                List<Point> points = GetPointsOnLine(eX + r, eY + r, dX + r, dY + r);
                SetColorsToBitmapPixels(outBitmap, points, SinogramValues[count,0]);

                //x,y - Di
                for (int i = 1; i < Detectors - 1; i++)
                {
                    dX = (int)(r * Math.Cos(GetRadians(alfa) + Math.PI - (GetRadians(BeamExtend) / 2) + i * (GetRadians(BeamExtend) / (Detectors - 1))));
                    dY = (int)(r * Math.Sin(GetRadians(alfa) + Math.PI - (GetRadians(BeamExtend) / 2) + i * (GetRadians(BeamExtend) / (Detectors - 1))));

                    points = GetPointsOnLine(eX + r, eY + r, dX + r, dY + r);
                    SetColorsToBitmapPixels(outBitmap, points, SinogramValues[count, i]);
                }

                //Dn-1
                dX = (int)(r * Math.Cos(GetRadians(alfa) + Math.PI + (GetRadians(BeamExtend) / 2)));
                dY = (int)(r * Math.Sin(GetRadians(alfa) + Math.PI + (GetRadians(BeamExtend) / 2)));

                points = GetPointsOnLine(eX + r, eY + r, dX + r, dY + r); // pobieramy punkty znajdujące się na linii emiter-detektor
                SetColorsToBitmapPixels(outBitmap, points, SinogramValues[count, Detectors - 1]);

                count++; // który scan w sinogramie
            }

            //przeskaluj
            // przypsiz do bitmapy


            return outBitmap;
        }


        private void SetColorsToBitmapPixels(Bitmap bitmap, List<Point> points, int value)
        {
            foreach (var point in points)
            {
                if (point.X > 0 && point.X < InBitmap.Width && point.Y > 0 && point.Y < InBitmap.Height)
                {
                    int rgb = value;
                    Color newColor = Color.FromArgb(rgb, rgb, rgb);
                    bitmap.SetPixel(point.X, point.Y, newColor);
                }
                
                // tu aktualziacja wartosci
            }
        }





        public Bitmap CreateSinogram()
        {
            int r = InBitmap.Width > InBitmap.Height  ? InBitmap.Width/2 : InBitmap.Height /2;
            double angle = 360 / (double)Scans;

            Bitmap tempSinogram = new Bitmap(Detectors, Scans);
           
            int count = 0;
            for (double alfa = 0; alfa < 360; alfa = alfa + angle)
            {
                //x,y - Emiter
                int eX = (int)(r * Math.Cos(GetRadians(alfa)));
                int eY = (int)(r * Math.Sin(GetRadians(alfa)));
               
                //x,y - D0 
                int dX = (int)(r * Math.Cos(GetRadians(alfa) + Math.PI - (GetRadians(BeamExtend) / 2)));
                int dY = (int)(r * Math.Sin(GetRadians(alfa) + Math.PI - (GetRadians(BeamExtend) / 2)));

                //Przy wyszukiwaniu punktów dodajemy do x i y "r", bo wzór jest ustawiony tak, że środek koła
                // znajduje się w punkcie (0,0). Dodając "r" przenosimy się w przestrzeń bitmapy tj. tylko pierwsza ćwiartka układu
                List<Point> points = GetPointsOnLine(eX + r, eY + r, dX + r, dY + r);
                int color = GetColorFromPoints(points);
                tempSinogram.SetPixel(0, count, Color.FromArgb(color, color, color));
                SinogramValues[count, 0] = color;
                //x,y - Di
                for (int i = 1; i < Detectors - 1; i++)
                {
                    dX = (int)(r * Math.Cos(GetRadians(alfa) + Math.PI - (GetRadians(BeamExtend) / 2) + i * (GetRadians(BeamExtend) / (Detectors - 1))));
                    dY = (int)(r * Math.Sin(GetRadians(alfa) + Math.PI - (GetRadians(BeamExtend) / 2) + i * (GetRadians(BeamExtend) / (Detectors - 1))));
                   
                    points = GetPointsOnLine(eX + r, eY + r, dX + r, dY + r);
                    color = GetColorFromPoints(points);
                    tempSinogram.SetPixel(i, count, Color.FromArgb(color, color, color));
                    SinogramValues[count, i] = color;
                }

                //Dn-1
                dX = (int)(r * Math.Cos(GetRadians(alfa) + Math.PI + (GetRadians(BeamExtend) / 2)));
                dY = (int)(r * Math.Sin(GetRadians(alfa) + Math.PI + (GetRadians(BeamExtend) / 2)));
               
                points = GetPointsOnLine(eX + r, eY + r, dX + r, dY + r); // pobieramy punkty znajdujące się na linii emiter-detektor
                color = GetColorFromPoints(points);// obliczamy kolor
                tempSinogram.SetPixel(Detectors - 1, count, Color.FromArgb(color, color, color));
                SinogramValues[count, Detectors - 1] = color;

                count ++; // który scan w sinogramie
            }

            
            //tu przeskaluje tablcie dwuwymairowowa 

            Bitmap sinogram = new Bitmap(Detectors, Scans);
          
            for (int i = 0; i < Detectors; i++)
            {
                for (int j =0; j < Scans; j++)
                {
                    //Odwracamy sinogram do odpowiedniej pozycji
                    var pixel = tempSinogram.GetPixel(Detectors - 1 - i, Scans - 1 - j);
                    sinogram.SetPixel(i, j, pixel);
                    //SinogramValues[j, i] = pixel.R;
                }
            }

            this.Sinogram = sinogram;
            return sinogram;
        }

        private double GetRadians(double angle)
        {
            return (Math.PI / 180) * angle;
        }

        private int GetColorFromPoints(List<Point> points)
        {
            int count = 0;
            int sum = 0;
            foreach (var point in points)
            {
                if (point.X > 0 && point.X < InBitmap.Width && point.Y > 0 && point.Y < InBitmap.Height)
                {
                    sum += InBitmap.GetPixel(point.X, point.Y).R; // sumujemy wartość 'wystarczy jedna bo dla rgb skali szarości wszystkie są równe'
                    count++;
                }
            }

            // TODO
            // trzeba ogarnąć to sumowanie, bo wymnożenie wyniku ostatecznego o 6 daje dopiero w miarę oczekiwany rezultat
            // 
            return Math.Min(sum / count *6  , 255); // dzielimy przez ilość punktów

            //TODO
            // wartosci walisz w tablice dwuwymairowa i przeskalowujesz na skale szarosci

        }

        private List<Point> GetPointsOnLine(int x0, int y0, int x1, int y1) // funkcja z neta, ale tej nie musieliśmy pisać sami
        {
            List<Point> points = new List<Point>();
            bool steep = Math.Abs(y1 - y0) > Math.Abs(x1 - x0);
            if (steep)
            {
                int t;
                t = x0; // swap x0 and y0
                x0 = y0;
                y0 = t;
                t = x1; // swap x1 and y1
                x1 = y1;
                y1 = t;
            }
            if (x0 > x1)
            {
                int t;
                t = x0; // swap x0 and x1
                x0 = x1;
                x1 = t;
                t = y0; // swap y0 and y1
                y0 = y1;
                y1 = t;
            }
            int dx = x1 - x0;
            int dy = Math.Abs(y1 - y0);
            int error = dx / 2;
            int ystep = (y0 < y1) ? 1 : -1;
            int y = y0;
            for (int x = x0; x <= x1; x++)
            {
                points.Add(new Point((steep ? y : x), (steep ? x : y)));
                error = error - dy;
                if (error < 0)
                {
                    y += ystep;
                    error += dx;
                }
            }
            return points;
        }



    }
}
